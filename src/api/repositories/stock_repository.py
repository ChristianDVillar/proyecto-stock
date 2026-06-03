"""Repositorio de Stock: solo acceso a datos (queries y persistencia)."""
from sqlalchemy import or_, func

from ..models import (
    db,
    Stock,
    StockMovement,
    StockStatusEnum,
    StockTypeEnum,
    CustomStockType,
)


class StockRepository:
    """Acceso a datos de Stock. Sin lógica de negocio."""

    @staticmethod
    def get_by_barcode(barcode: str, include_deleted: bool = False):
        q = Stock.query.filter_by(barcode=barcode)
        if not include_deleted:
            q = q.filter(Stock.deleted_at.is_(None))
        return q.first()

    @staticmethod
    def get_by_id(stock_id: int, include_deleted: bool = False):
        q = Stock.query.filter_by(id=stock_id)
        if not include_deleted:
            q = q.filter(Stock.deleted_at.is_(None))
        return q.first()

    @staticmethod
    def exists_barcode(barcode: str, tenant_id=None) -> bool:
        q = Stock.query.filter_by(barcode=barcode)
        if tenant_id is not None:
            q = q.filter_by(tenant_id=tenant_id)
        return q.first() is not None

    @staticmethod
    def add(stock: Stock) -> Stock:
        db.session.add(stock)
        db.session.flush()
        return stock

    @staticmethod
    def add_movement(movement: StockMovement) -> StockMovement:
        db.session.add(movement)
        return movement

    @staticmethod
    def soft_delete(stock_id: int) -> Stock | None:
        stock = Stock.query.filter_by(id=stock_id).first()
        if not stock:
            return None
        from datetime import datetime
        stock.deleted_at = datetime.utcnow()
        db.session.add(stock)
        return stock

    @staticmethod
    def list_active():
        return Stock.query.filter(Stock.deleted_at.is_(None)).all()

    @staticmethod
    def inventory_by_device():
        """Agrupa por dispositivo (solo activos)."""
        return (
            db.session.query(
                Stock.dispositivo,
                func.count(Stock.id).label('total_items'),
                func.sum(Stock.cantidad).label('total_quantity'),
            )
            .filter(Stock.deleted_at.is_(None))
            .group_by(Stock.dispositivo)
            .all()
        )

    @staticmethod
    def search(
        query: str = '',
        stocktype: str = None,
        status: str = None,
        location: str = None,
        page: int = 1,
        per_page: int = 20,
    ):
        per_page = min(per_page, 100)
        q = Stock.query.filter(Stock.deleted_at.is_(None))
        if query:
            q = q.filter(
                or_(
                    Stock.barcode.ilike(f'%{query}%'),
                    Stock.inventario.ilike(f'%{query}%'),
                    Stock.modelo.ilike(f'%{query}%'),
                    Stock.descripcion.ilike(f'%{query}%'),
                )
            )
        if stocktype:
            try:
                if stocktype.startswith('custom_'):
                    custom_id = int(stocktype.split('_')[1])
                    if CustomStockType.query.get(custom_id):
                        q = q.filter(Stock.stocktype == StockTypeEnum.otro)
                else:
                    q = q.filter(Stock.stocktype == StockTypeEnum[stocktype])
            except (KeyError, ValueError, IndexError):
                pass
        if status:
            try:
                q = q.filter(Stock.status == StockStatusEnum[status])
            except KeyError:
                pass
        if location:
            q = q.filter(Stock.location.ilike(f'%{location}%'))
        total_items = q.count()
        total_pages = (total_items + per_page - 1) // per_page
        items = (
            q.order_by(Stock.updated_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        return items, total_items, total_pages
