"""Dashboard ejecutivo: KPIs, vencimientos, stock bajo, movimientos."""
from datetime import datetime, timedelta
from sqlalchemy import func

from ..models import (
    db, Stock, StockMovement, StockTypeEnum, Supplier,
)
from ..tenant_utils import get_current_tenant_id


def _enum_value(obj):
    return obj.value if hasattr(obj, 'value') else str(obj)


def _active_stock_query():
    q = Stock.query.filter(Stock.deleted_at.is_(None))
    tid = get_current_tenant_id()
    if tid is not None:
        q = q.filter(Stock.tenant_id == tid)
    return q


class DashboardService:
    @staticmethod
    def get_executive_summary():
        today = datetime.utcnow().date()
        active = _active_stock_query()

        total_items = active.count()
        total_units = db.session.query(func.coalesce(func.sum(Stock.cantidad), 0)).filter(
            Stock.deleted_at.is_(None),
            *([Stock.tenant_id == get_current_tenant_id()] if get_current_tenant_id() else []),
        ).scalar() or 0

        inventory_value = db.session.query(
            func.coalesce(func.sum(Stock.cantidad * func.coalesce(Stock.unit_cost, 0)), 0)
        ).filter(
            Stock.deleted_at.is_(None),
            *([Stock.tenant_id == get_current_tenant_id()] if get_current_tenant_id() else []),
        ).scalar() or 0

        # Inventario por categoría
        cat_q = db.session.query(Stock.dispositivo, func.count(Stock.id), func.sum(Stock.cantidad)).filter(
            Stock.deleted_at.is_(None),
            *([Stock.tenant_id == get_current_tenant_id()] if get_current_tenant_id() else []),
        )
        by_category = cat_q.group_by(Stock.dispositivo).all()
        category_total = sum(c or 0 for _, c, _ in by_category) or 1
        inventory_by_category = [
            {
                'category': _enum_value(t) if t else 'otros',
                'count': count,
                'units': int(units or 0),
                'percentage': round((count / category_total) * 100, 1),
            }
            for t, count, units in by_category
        ]

        # Stock bajo / crítico
        low_stock = []
        critical_stock = []
        for s in active.all():
            level = s.stock_level()
            item = s.to_summary_dict()
            if level == 'bajo':
                low_stock.append(item)
            elif level == 'critico':
                critical_stock.append(item)

        # Vencimientos
        expiring_soon = []
        expired = []
        for s in active.filter(Stock.expiration_date.isnot(None)).all():
            alert = s.expiration_alert()
            if alert == 'vencido':
                expired.append(s.to_summary_dict())
            elif alert in ('7_dias', '30_dias', '90_dias'):
                expiring_soon.append({**s.to_summary_dict(), 'alert_level': alert})

        expiring_soon.sort(key=lambda x: x.get('days_until_expiration') or 9999)

        # Garantías próximas (30 días)
        warranty_alerts = []
        for s in active.filter(Stock.warranty_expiry.isnot(None)).all():
            days = s.warranty_days_remaining()
            if days is not None and days <= 30:
                warranty_alerts.append({**s.to_summary_dict(), 'warranty_days': days})
        warranty_alerts.sort(key=lambda x: x.get('warranty_days') or 9999)

        # Movimientos últimos 30 días
        since = datetime.utcnow() - timedelta(days=30)
        stock_ids = [s.id for s in active.with_entities(Stock.id).all()]
        movements = StockMovement.query.filter(
            StockMovement.timestamp >= since,
            StockMovement.stock_id.in_(stock_ids) if stock_ids else False,
        ).all() if stock_ids else []
        entradas = sum(m.quantity for m in movements if m.movement_type == 'entrada')
        salidas = sum(m.quantity for m in movements if m.movement_type == 'salida')

        tid = get_current_tenant_id()
        suppliers_q = Supplier.query.filter_by(is_active=True)
        if tid is not None:
            suppliers_q = suppliers_q.filter(Supplier.tenant_id == tid)
        suppliers_count = suppliers_q.count()

        # Costes y márgenes
        stocks = active.all()
        total_potential_profit = sum(s.potential_profit() or 0 for s in stocks)
        margins = [s.margin_percent() for s in stocks if s.margin_percent() is not None]
        avg_margin_percent = round(sum(margins) / len(margins), 1) if margins else None
        inventory_at_sale = sum(
            (s.sale_price or 0) * (s.cantidad or 0) for s in stocks if s.sale_price
        )

        return {
            'kpis': {
                'total_items': total_items,
                'total_units': int(total_units),
                'inventory_value': round(float(inventory_value), 2),
                'inventory_at_sale_value': round(float(inventory_at_sale), 2),
                'potential_profit': round(float(total_potential_profit), 2),
                'average_margin_percent': avg_margin_percent,
                'suppliers_count': suppliers_count,
                'low_stock_count': len(low_stock),
                'critical_stock_count': len(critical_stock),
                'expiring_soon_count': len(expiring_soon),
                'expired_count': len(expired),
                'warranty_alerts_count': len(warranty_alerts),
            },
            'inventory_by_category': inventory_by_category,
            'movements_summary': {
                'period_days': 30,
                'entradas': entradas,
                'salidas': salidas,
            },
            'low_stock': low_stock[:50],
            'critical_stock': critical_stock[:50],
            'expiring_soon': expiring_soon[:50],
            'expired': expired[:50],
            'warranty_alerts': warranty_alerts[:50],
        }

    @staticmethod
    def get_expiration_alerts():
        """Alertas agrupadas: 90, 30, 7 días y vencido."""
        active = _active_stock_query().filter(Stock.expiration_date.isnot(None)).all()
        buckets = {'90_dias': [], '30_dias': [], '7_dias': [], 'vencido': []}
        for s in active:
            alert = s.expiration_alert()
            if alert and alert in buckets:
                buckets[alert].append(s.to_summary_dict())
        for key in buckets:
            buckets[key].sort(key=lambda x: x.get('days_until_expiration') or 9999)
        return buckets
