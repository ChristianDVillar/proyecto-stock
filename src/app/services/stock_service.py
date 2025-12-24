"""
Stock business logic service
Separates business logic from routes
"""
from sqlalchemy import or_
from api.models import db, Stock, StockStatusEnum, StockTypeEnum, CustomStockType
from api.utils import validate_barcode, validate_inventario, validate_modelo, validate_cantidad


class StockService:
    """Service for stock operations"""
    
    @staticmethod
    def create_stock(data, user_id):
        """
        Create a new stock item
        Returns: (success: bool, data: dict, error: str)
        """
        # Validate required fields
        required_fields = ['barcode', 'inventario', 'dispositivo', 'modelo']
        for field in required_fields:
            if not data.get(field):
                return False, None, f'Campo requerido faltante: {field}'
        
        # Validate formats
        barcode_valid, barcode_error = validate_barcode(data['barcode'])
        if not barcode_valid:
            return False, None, barcode_error
        
        inventario_valid, inventario_error = validate_inventario(data['inventario'])
        if not inventario_valid:
            return False, None, inventario_error
        
        modelo_valid, modelo_error = validate_modelo(data['modelo'])
        if not modelo_valid:
            return False, None, modelo_error
        
        cantidad_valid, cantidad_error = validate_cantidad(data.get('cantidad', 1))
        if not cantidad_valid:
            return False, None, cantidad_error
        
        # Check for duplicate barcode
        existing_stock = Stock.query.filter_by(barcode=data['barcode']).first()
        if existing_stock:
            return False, None, 'El código de barras ya existe'
        
        # Process device type
        device_type = data.get('dispositivo', '').lower()
        device_type_enum = None
        
        try:
            device_type_enum = StockTypeEnum[device_type]
        except KeyError:
            if device_type.startswith('custom_'):
                try:
                    custom_id = int(device_type.split('_')[1])
                    custom_type = CustomStockType.query.get(custom_id)
                    if not custom_type:
                        return False, None, 'Tipo personalizado no encontrado'
                    device_type_enum = StockTypeEnum.otro
                except (IndexError, ValueError):
                    return False, None, 'Formato de tipo personalizado inválido'
            else:
                return False, None, f'Tipo de dispositivo inválido: {device_type}'
        
        # Create stock
        try:
            from datetime import datetime
            
            new_stock = Stock(
                barcode=data['barcode'],
                inventario=data['inventario'],
                dispositivo=device_type_enum,
                modelo=data['modelo'],
                descripcion=data.get('descripcion', ''),
                cantidad=int(data.get('cantidad', 1)),
                stocktype=device_type_enum,
                status=StockStatusEnum.disponible,
                location=data.get('location', 'default'),
                serial_number=data.get('serial_number'),
                purchase_date=datetime.strptime(data['purchase_date'], '%Y-%m-%d').date() if data.get('purchase_date') else None,
                warranty_expiry=datetime.strptime(data['warranty_expiry'], '%Y-%m-%d').date() if data.get('warranty_expiry') else None,
                created_by=user_id
            )
            
            db.session.add(new_stock)
            db.session.commit()
            
            return True, {
                'id': new_stock.id,
                'barcode': new_stock.barcode
            }, None
            
        except Exception as e:
            db.session.rollback()
            return False, None, f'Error al crear stock: {str(e)}'
    
    @staticmethod
    def search_stocks(query_params):
        """
        Search stocks with filters and pagination
        Returns: (stocks: list, total_items: int, total_pages: int)
        """
        from api.models import StockMovement
        
        query = query_params.get('q', '')
        stocktype = query_params.get('type')
        status = query_params.get('status')
        location = query_params.get('location')
        page = query_params.get('page', 1)
        per_page = min(query_params.get('per_page', 20), 100)
        
        stock_query = Stock.query
        
        # Apply search query
        if query:
            stock_query = stock_query.filter(
                or_(
                    Stock.barcode.ilike(f'%{query}%'),
                    Stock.inventario.ilike(f'%{query}%'),
                    Stock.modelo.ilike(f'%{query}%'),
                    Stock.descripcion.ilike(f'%{query}%')
                )
            )
        
        # Apply filters
        if stocktype:
            try:
                if stocktype.startswith('custom_'):
                    custom_id = int(stocktype.split('_')[1])
                    custom_type = CustomStockType.query.get(custom_id)
                    if custom_type:
                        stock_query = stock_query.filter(Stock.stocktype == StockTypeEnum.otro)
                else:
                    stock_type_enum = StockTypeEnum[stocktype]
                    stock_query = stock_query.filter(Stock.stocktype == stock_type_enum)
            except (KeyError, ValueError, IndexError):
                pass
        
        if status:
            try:
                status_enum = StockStatusEnum[status]
                stock_query = stock_query.filter(Stock.status == status_enum)
            except KeyError:
                pass
        
        if location:
            stock_query = stock_query.filter(Stock.location.ilike(f'%{location}%'))
        
        # Count total
        total_items = stock_query.count()
        total_pages = (total_items + per_page - 1) // per_page
        
        # Paginate
        stocks = stock_query.order_by(Stock.updated_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        ).items
        
        return stocks, total_items, total_pages

