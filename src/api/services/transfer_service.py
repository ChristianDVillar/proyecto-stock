"""Transferencias entre almacenes."""
from datetime import datetime

from ..models import (
    db, Stock, Warehouse, WarehouseTransfer, TransferStatusEnum,
    StockMovement, AssetEvent, AssetEventTypeEnum,
)
from ..tenant_utils import get_current_tenant_id


class TransferService:
    @staticmethod
    def list_transfers(tenant_id=None, page=1, per_page=20):
        tid = tenant_id or get_current_tenant_id()
        q = WarehouseTransfer.query.filter_by(tenant_id=tid).order_by(
            WarehouseTransfer.created_at.desc()
        )
        per_page = min(max(1, per_page), 100)
        pagination = q.paginate(page=page, per_page=per_page, error_out=False)
        items = [t.to_dict() for t in pagination.items]
        return {
            'items': items,
            'transfers': items,
            'total': pagination.total,
            'page': page,
            'pages': pagination.pages or 1,
            'per_page': per_page,
        }

    @staticmethod
    def create_transfer(stock_id, from_wh_id, to_wh_id, quantity, user_id, notes=None):
        tid = get_current_tenant_id()
        if from_wh_id == to_wh_id:
            return None, {'error': 'Origen y destino deben ser distintos', 'status': 400}

        stock = Stock.query.filter_by(id=stock_id, tenant_id=tid).filter(
            Stock.deleted_at.is_(None)
        ).first()
        if not stock:
            return None, {'error': 'Stock no encontrado', 'status': 404}
        if quantity <= 0:
            return None, {'error': 'Cantidad inválida', 'status': 400}
        # v1: transferencia mueve el ítem completo al otro almacén
        if quantity != stock.cantidad:
            return None, {'error': 'Transferencia parcial no soportada; use la cantidad total del stock', 'status': 400}

        from_wh = Warehouse.query.filter_by(id=from_wh_id, tenant_id=tid, is_active=True).first()
        to_wh = Warehouse.query.filter_by(id=to_wh_id, tenant_id=tid, is_active=True).first()
        if not from_wh or not to_wh:
            return None, {'error': 'Almacén no encontrado', 'status': 404}

        transfer = WarehouseTransfer(
            tenant_id=tid,
            stock_id=stock_id,
            from_warehouse_id=from_wh_id,
            to_warehouse_id=to_wh_id,
            quantity=quantity,
            requested_by=user_id,
            notes=notes,
            status=TransferStatusEnum.pendiente,
        )
        db.session.add(transfer)
        return transfer, None

    @staticmethod
    def complete_transfer(transfer_id, user_id):
        tid = get_current_tenant_id()
        transfer = WarehouseTransfer.query.filter_by(id=transfer_id, tenant_id=tid).first()
        if not transfer:
            return None, {'error': 'Transferencia no encontrada', 'status': 404}
        if transfer.status != TransferStatusEnum.pendiente:
            return None, {'error': 'La transferencia ya fue procesada', 'status': 400}

        stock = Stock.query.get(transfer.stock_id)
        if not stock or stock.cantidad < transfer.quantity:
            return None, {'error': 'Stock insuficiente', 'status': 400}

        # Un movimiento de trazabilidad (no altera cantidad total)
        mov = StockMovement(
            stock_id=stock.id,
            user_id=user_id,
            quantity=transfer.quantity,
            movement_type='transferencia',
            from_location=transfer.from_warehouse.name if transfer.from_warehouse else 'origen',
            to_location=transfer.to_warehouse.name if transfer.to_warehouse else 'destino',
            notes=transfer.notes or f'Transferencia #{transfer.id}',
        )
        db.session.add(mov)

        stock.warehouse_id = transfer.to_warehouse_id
        stock.location = transfer.to_warehouse.code if transfer.to_warehouse else stock.location

        transfer.status = TransferStatusEnum.completada
        transfer.completed_by = user_id
        transfer.completed_at = datetime.utcnow()

        evt = AssetEvent(
            stock_id=stock.id,
            user_id=user_id,
            event_type=AssetEventTypeEnum.transferencia,
            description=f'Transferencia {transfer.from_warehouse.name} → {transfer.to_warehouse.name} ({transfer.quantity} uds)',
        )
        db.session.add(evt)
        return transfer, None
