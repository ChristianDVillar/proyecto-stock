"""Órdenes de compra: generación, aprobación, recepción."""
from datetime import datetime

from ..models import (
    db, Stock, Supplier, PurchaseOrder, PurchaseOrderLine,
    PurchaseOrderStatusEnum, StockMovement, AssetEvent, AssetEventTypeEnum,
)
from ..tenant_utils import get_current_tenant_id, scope_tenant
from .stock_service import record_stock_history, _stock_to_snapshot


def _next_order_number(tenant_id=None):
    tid = tenant_id or get_current_tenant_id()
    year = datetime.utcnow().year
    q = PurchaseOrder.query.filter(PurchaseOrder.order_number.like(f'OC-{year}-%'))
    if tid is not None:
        q = q.filter(PurchaseOrder.tenant_id == tid)
    count = q.count()
    return f'OC-{year}-{count + 1:04d}'


def _orders_query():
    return scope_tenant(PurchaseOrder.query, PurchaseOrder)


class PurchaseOrderService:
    @staticmethod
    def list_orders(page=1, per_page=20, status=None):
        per_page = min(max(1, per_page), 100)
        q = _orders_query().order_by(PurchaseOrder.created_at.desc())
        if status:
            try:
                st = PurchaseOrderStatusEnum[status]
                q = q.filter(PurchaseOrder.status == st)
            except KeyError:
                pass
        pagination = q.paginate(page=page, per_page=per_page, error_out=False)
        return {
            'items': [o.to_dict() for o in pagination.items],
            'purchase_orders': [o.to_dict() for o in pagination.items],
            'total': pagination.total,
            'page': page,
            'pages': pagination.pages or 1,
            'per_page': per_page,
        }

    @staticmethod
    def get_order(order_id):
        return _orders_query().filter(PurchaseOrder.id == order_id).first()

    @staticmethod
    def generate_from_low_stock(supplier_id, created_by_id, notes=None):
        """Genera OC con líneas de productos bajo stock mínimo."""
        tid = get_current_tenant_id()
        supplier = scope_tenant(Supplier.query, Supplier, tid).filter(Supplier.id == supplier_id).first()
        if not supplier or not supplier.is_active:
            return None, {'error': 'Proveedor no encontrado', 'status': 404}

        low_items = []
        stock_q = Stock.query.filter(Stock.deleted_at.is_(None))
        if tid is not None:
            stock_q = stock_q.filter(Stock.tenant_id == tid)
        for s in stock_q.all():
            if s.stock_level() in ('bajo', 'critico') and s.minimum_stock:
                qty_needed = max((s.optimal_stock or s.minimum_stock) - s.cantidad, 1)
                low_items.append((s, qty_needed))

        if not low_items:
            return None, {'error': 'No hay productos bajo stock mínimo', 'status': 400}

        order = PurchaseOrder(
            tenant_id=tid,
            order_number=_next_order_number(tid),
            supplier_id=supplier_id,
            status=PurchaseOrderStatusEnum.pendiente,
            created_by=created_by_id,
            notes=notes,
        )
        db.session.add(order)
        db.session.flush()

        total = 0.0
        for stock, qty in low_items:
            cost = stock.unit_cost or 0
            line = PurchaseOrderLine(
                purchase_order_id=order.id,
                stock_id=stock.id,
                description=f'{stock.modelo} ({stock.barcode})',
                quantity_ordered=qty,
                unit_cost=cost,
                barcode=stock.barcode,
            )
            db.session.add(line)
            total += cost * qty
        order.total_amount = total
        return order, None

    @staticmethod
    def create_manual(supplier_id, created_by_id, lines, notes=None):
        tid = get_current_tenant_id()
        supplier = scope_tenant(Supplier.query, Supplier, tid).filter(Supplier.id == supplier_id).first()
        if not supplier:
            return None, {'error': 'Proveedor no encontrado', 'status': 404}
        if not lines:
            return None, {'error': 'La orden debe tener al menos una línea', 'status': 400}

        order = PurchaseOrder(
            tenant_id=tid,
            order_number=_next_order_number(tid),
            supplier_id=supplier_id,
            status=PurchaseOrderStatusEnum.borrador,
            created_by=created_by_id,
            notes=notes,
        )
        db.session.add(order)
        db.session.flush()

        total = 0.0
        for ln in lines:
            qty = int(ln.get('quantity_ordered', 0))
            if qty <= 0:
                continue
            cost = float(ln.get('unit_cost') or 0)
            line = PurchaseOrderLine(
                purchase_order_id=order.id,
                stock_id=ln.get('stock_id'),
                description=ln.get('description', 'Producto'),
                quantity_ordered=qty,
                unit_cost=cost,
                barcode=ln.get('barcode'),
            )
            db.session.add(line)
            total += cost * qty
        order.total_amount = total
        return order, None

    @staticmethod
    def approve(order_id, approver_id):
        order = _orders_query().filter(PurchaseOrder.id == order_id).first()
        if not order:
            return None, {'error': 'Orden no encontrada', 'status': 404}
        if order.status not in (PurchaseOrderStatusEnum.borrador, PurchaseOrderStatusEnum.pendiente):
            return None, {'error': 'La orden no puede aprobarse en este estado', 'status': 400}
        order.status = PurchaseOrderStatusEnum.aprobada
        order.approved_by = approver_id
        order.approved_at = datetime.utcnow()
        return order, None

    @staticmethod
    def receive(order_id, user_id):
        """Recibe mercancía: entrada automática de stock."""
        order = _orders_query().filter(PurchaseOrder.id == order_id).first()
        if not order:
            return None, {'error': 'Orden no encontrada', 'status': 404}
        if order.status != PurchaseOrderStatusEnum.aprobada:
            return None, {'error': 'Solo se pueden recibir órdenes aprobadas', 'status': 400}

        for line in order.lines:
            qty = line.quantity_ordered - (line.quantity_received or 0)
            if qty <= 0:
                continue
            if line.stock_id:
                stock = Stock.query.get(line.stock_id)
                if stock and stock.deleted_at is None:
                    old_snap = _stock_to_snapshot(stock)
                    movement = StockMovement(
                        stock_id=stock.id,
                        user_id=user_id,
                        quantity=qty,
                        movement_type='entrada',
                        to_location=stock.location,
                        notes=f'Recepción OC {order.order_number}',
                    )
                    db.session.add(movement)
                    if line.unit_cost:
                        stock.unit_cost = line.unit_cost
                    line.quantity_received = (line.quantity_received or 0) + qty
                    record_stock_history(stock.id, user_id, 'purchase_receive', old_value=old_snap, new_value=_stock_to_snapshot(stock))
                    evt = AssetEvent(
                        stock_id=stock.id,
                        user_id=user_id,
                        event_type=AssetEventTypeEnum.comprado,
                        description=f'Recepción OC {order.order_number}: +{qty} unidades',
                    )
                    db.session.add(evt)
            line.quantity_received = line.quantity_ordered

        order.status = PurchaseOrderStatusEnum.recibida
        order.received_at = datetime.utcnow()
        return order, None
