"""Servicio de stock: lógica de negocio; delega acceso a datos al repositorio."""
import json
from datetime import datetime

from ..models import (
    db, Stock, StockMovement, MaintenanceRecord, StockHistory,
    StockStatusEnum, StockTypeEnum, CustomStockType, DeviceTypeEnum, CustomDeviceType
)
from ..repositories.stock_repository import StockRepository


def _stock_to_snapshot(stock):
    """Serializa un Stock a dict para historial (sin relaciones)."""
    if not stock:
        return None
    return {
        'id': stock.id,
        'barcode': stock.barcode,
        'inventario': stock.inventario,
        'modelo': stock.modelo,
        'cantidad': getattr(stock, 'cantidad', None),
        'status': stock.status.value if hasattr(stock.status, 'value') else str(stock.status),
        'location': stock.location,
        'updated_at': stock.updated_at.isoformat() if getattr(stock, 'updated_at', None) else None,
    }


def record_stock_history(stock_id: int, user_id: int, action: str, old_value: dict = None, new_value: dict = None):
    """Registra una entrada en stock_history para auditoría."""
    entry = StockHistory(
        stock_id=stock_id,
        changed_by=user_id,
        action=action,
        old_value=json.dumps(old_value) if old_value is not None else None,
        new_value=json.dumps(new_value) if new_value is not None else None,
    )
    db.session.add(entry)


def _enum_value(obj):
    """Valor de un campo enum para API."""
    return obj.value if hasattr(obj, 'value') else str(obj)


class StockService:
    @staticmethod
    def format_stock_detail(stock, movements=None, last_maintenance=None):
        """
        Serializa un Stock con movimientos y último mantenimiento para la API.
        movements: lista de StockMovement; last_maintenance: MaintenanceRecord o None.
        """
        if not stock:
            return None
        payload = {
            'stock': {
                'id': stock.id,
                'barcode': stock.barcode,
                'inventario': stock.inventario,
                'dispositivo': _enum_value(stock.dispositivo),
                'modelo': stock.modelo,
                'descripcion': stock.descripcion,
                'cantidad': stock.cantidad,
                'stocktype': stock.stocktype.value,
                'status': stock.status.value,
                'location': stock.location,
                'serial_number': stock.serial_number,
                'purchase_date': stock.purchase_date.isoformat() if stock.purchase_date else None,
                'warranty_expiry': stock.warranty_expiry.isoformat() if stock.warranty_expiry else None,
                'last_maintenance': stock.last_maintenance.isoformat() if stock.last_maintenance else None,
                'next_maintenance': stock.next_maintenance.isoformat() if stock.next_maintenance else None,
                'image_url': stock.image_url,
            },
            'movements': [{
                'type': m.movement_type,
                'quantity': m.quantity,
                'timestamp': m.timestamp.isoformat(),
                'from_location': m.from_location,
                'to_location': m.to_location,
                'notes': m.notes,
            } for m in (movements or [])],
            'last_maintenance': None,
        }
        if last_maintenance:
            payload['last_maintenance'] = {
                'type': last_maintenance.maintenance_type,
                'date': last_maintenance.date_performed.isoformat(),
                'description': last_maintenance.description,
                'status': last_maintenance.status,
            }
        return payload
    @staticmethod
    def create_stock_item(created_by_id, data: dict):
        """
        Crea un ítem de stock y movimiento inicial. Devuelve (stock, error_dict).
        error_dict es None si todo bien; si no, {'error': str, 'message': str, 'status': int}.
        """
        from ..utils import (
            validate_barcode, validate_inventario, validate_modelo, validate_cantidad,
            validate_descripcion, validate_request_data
        )
        # Normalizar entradas: strings como str y trim
        def _str(v, default=''):
            if v is None:
                return default
            return str(v).strip() if isinstance(v, str) else str(v)
        barcode = _str(data.get('barcode'))
        inventario = _str(data.get('inventario'))
        modelo = _str(data.get('modelo'))
        descripcion = _str(data.get('descripcion'), '')

        required = ['barcode', 'inventario', 'dispositivo', 'modelo']
        if not barcode or not inventario or not data.get('dispositivo') or not modelo:
            missing = [f for f in required if not (data.get(f) and _str(data.get(f)))]
            return None, {'error': 'Datos inválidos', 'message': f"Faltan o están vacíos: {', '.join(missing)}", 'status': 400}
        barcode_valid, barcode_error = validate_barcode(barcode)
        if not barcode_valid:
            return None, {'error': 'Código de barras inválido', 'message': barcode_error, 'status': 400}
        inventario_valid, inventario_error = validate_inventario(inventario)
        if not inventario_valid:
            return None, {'error': 'Código de inventario inválido', 'message': inventario_error, 'status': 400}
        modelo_valid, modelo_error = validate_modelo(modelo)
        if not modelo_valid:
            return None, {'error': 'Modelo inválido', 'message': modelo_error, 'status': 400}
        descripcion_valid, descripcion_error = validate_descripcion(descripcion)
        if not descripcion_valid:
            return None, {'error': 'Descripción inválida', 'message': descripcion_error, 'status': 400}

        if StockRepository.exists_barcode(barcode):
            return None, {'error': 'Código de barras duplicado', 'message': 'El código de barras ya existe.', 'status': 400}

        device_type = _str(data.get('dispositivo')).lower()
        device_type_enum = None
        custom_type = None
        try:
            device_type_enum = StockTypeEnum[device_type]
        except KeyError:
            if device_type.startswith('custom_'):
                try:
                    custom_type_id = int(device_type.split('_')[1])
                    custom_type = CustomStockType.query.get(custom_type_id)
                    if not custom_type:
                        return None, {'error': 'Tipo personalizado no encontrado', 'message': 'El tipo no existe.', 'status': 400}
                    device_type_enum = StockTypeEnum.otro
                except (IndexError, ValueError):
                    return None, {'error': 'Formato de tipo inválido', 'message': 'Formato inválido.', 'status': 400}
            else:
                return None, {'error': 'Tipo de dispositivo inválido', 'message': f'"{device_type}" no válido.', 'status': 400}

        try:
            cantidad_raw = data.get('cantidad', 1)
            cantidad = int(cantidad_raw) if cantidad_raw not in (None, '') else 1
        except (TypeError, ValueError):
            cantidad = 1
        cantidad_valid, cantidad_error = validate_cantidad(cantidad)
        if not cantidad_valid:
            return None, {'error': 'Cantidad inválida', 'message': cantidad_error, 'status': 400}

        purchase_date = None
        if data.get('purchase_date'):
            try:
                purchase_date = datetime.strptime(data['purchase_date'], '%Y-%m-%d').date()
            except ValueError:
                pass
        warranty_expiry = None
        if data.get('warranty_expiry'):
            try:
                warranty_expiry = datetime.strptime(data['warranty_expiry'], '%Y-%m-%d').date()
            except ValueError:
                pass

        try:
            # Alta de stock, movimiento inicial y auditoría (misma transacción del request)
            new_stock = Stock(
                barcode=barcode,
                inventario=inventario,
                dispositivo=device_type_enum,
                modelo=modelo,
                descripcion=descripcion or None,
                cantidad=cantidad,
                stocktype=device_type_enum,
                status=StockStatusEnum.disponible,
                location=_str(data.get('location')) or 'default',
                serial_number=_str(data.get('serial_number')) or None,
                purchase_date=purchase_date,
                warranty_expiry=warranty_expiry,
                created_by=created_by_id
            )
            StockRepository.add(new_stock)

            movement = StockMovement(
                user_id=created_by_id,
                quantity=cantidad,
                movement_type='entrada',
                to_location=_str(data.get('location')) or 'default',
                notes='Registro inicial de inventario'
            )
            movement.stock_id = new_stock.id
            StockRepository.add_movement(movement)

            record_stock_history(new_stock.id, created_by_id, 'create', old_value=None, new_value=_stock_to_snapshot(new_stock))

            return new_stock, None
        except Exception as e:
            msg = str(e) or type(e).__name__
            return None, {'error': 'Error al crear el stock', 'message': msg, 'status': 500}

    @staticmethod
    def get_inventory():
        """Resumen y detalle de inventario (para listado)."""
        inventory = StockRepository.inventory_by_device()
        inventory_data = [
            {'tipo': _enum_value(t) if t else 'Desconocido', 'total_items': i, 'total_cantidad': c}
            for t, i, c in inventory
        ]
        stock_items = StockRepository.list_active()
        stock_details = [
            {
                'id': s.id, 'barcode': s.barcode, 'inventario': s.inventario,
                'dispositivo': _enum_value(s.dispositivo), 'modelo': s.modelo,
                'cantidad': s.cantidad, 'status': _enum_value(s.status), 'location': s.location
            }
            for s in stock_items
        ]
        return {'resumen': inventory_data, 'detalle': stock_details}

    @staticmethod
    def search_stock(query='', stocktype=None, status=None, location=None, page=1, per_page=20):
        """Búsqueda paginada (excluye soft-deleted). per_page se limita a 100."""
        per_page = min(per_page, 100)
        items, total_items, total_pages = StockRepository.search(
            query=query, stocktype=stocktype, status=status, location=location,
            page=page, per_page=per_page
        )
        return {
            'stocks': [{
                'id': s.id, 'barcode': s.barcode, 'inventario': s.inventario,
                'dispositivo': _enum_value(s.dispositivo), 'modelo': s.modelo,
                'cantidad': s.cantidad, 'status': _enum_value(s.status), 'location': s.location
            } for s in items],
            'total_items': total_items,
            'total_pages': total_pages,
            'current_page': page,
            'per_page': per_page
        }

    @staticmethod
    def soft_delete_stock(stock_id: int, user_id: int):
        """
        Soft delete: marca deleted_at y registra en historial.
        Devuelve (stock, error_dict). error_dict es None si ok.
        """
        stock = StockRepository.get_by_id(stock_id, include_deleted=False)
        if not stock:
            return None, {'error': 'Stock no encontrado', 'status': 404}
        old_snapshot = _stock_to_snapshot(stock)
        try:
            StockRepository.soft_delete(stock_id)
            record_stock_history(stock_id, user_id, 'soft_delete', old_value=old_snapshot, new_value=None)
            return stock, None
        except Exception as e:
            return None, {'error': 'Error al eliminar', 'message': str(e), 'status': 500}