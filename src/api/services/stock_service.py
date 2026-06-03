"""Servicio de stock: lógica de negocio; delega acceso a datos al repositorio."""
import json
from datetime import datetime

from ..models import (
    db, Stock, StockMovement, MaintenanceRecord, StockHistory,
    StockStatusEnum, StockTypeEnum, CustomStockType, DeviceTypeEnum, CustomDeviceType,
    AssetEvent, AssetEventTypeEnum,
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
            'stock': stock.to_summary_dict(),
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
        from ..tenant_utils import get_current_user, assign_user_tenant
        from ..models import Warehouse
        creator = get_current_user()
        tenant_id = creator.tenant_id if creator else None
        if creator and not tenant_id:
            tenant_id = assign_user_tenant(creator)
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

        if StockRepository.exists_barcode(barcode, tenant_id=tenant_id):
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

        def _parse_date(key):
            v = data.get(key)
            if not v:
                return None
            try:
                return datetime.strptime(v, '%Y-%m-%d').date()
            except ValueError:
                return None

        def _bool(key):
            return bool(data.get(key))

        def _int_opt(key):
            v = data.get(key)
            if v in (None, ''):
                return None
            try:
                return int(v)
            except (TypeError, ValueError):
                return None

        def _float_opt(key):
            v = data.get(key)
            if v in (None, ''):
                return None
            try:
                return float(v)
            except (TypeError, ValueError):
                return None

        expiration_date = _parse_date('expiration_date')
        batch_number = _str(data.get('batch_number')) or None
        supplier_id = data.get('supplier_id')
        if supplier_id:
            try:
                supplier_id = int(supplier_id)
            except (TypeError, ValueError):
                supplier_id = None

        try:
            default_wh = None
            if tenant_id:
                default_wh = Warehouse.query.filter_by(tenant_id=tenant_id, is_default=True).first()

            new_stock = Stock(
                tenant_id=tenant_id,
                warehouse_id=default_wh.id if default_wh else None,
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
                expiration_date=expiration_date,
                batch_number=batch_number,
                supplier_id=supplier_id,
                minimum_stock=_int_opt('minimum_stock') or 0,
                optimal_stock=_int_opt('optimal_stock'),
                unit_cost=_float_opt('unit_cost') or _float_opt('purchase_price'),
                purchase_price=_float_opt('purchase_price') or _float_opt('unit_cost'),
                sale_price=_float_opt('sale_price'),
                average_cost=_float_opt('average_cost') or _float_opt('purchase_price') or _float_opt('unit_cost'),
                location_code=_str(data.get('location_code')) or None,
                location_aisle=_str(data.get('location_aisle')) or None,
                location_shelf=_str(data.get('location_shelf')) or None,
                contains_gluten=_bool('contains_gluten'),
                contains_milk=_bool('contains_milk'),
                contains_nuts=_bool('contains_nuts'),
                contains_soy=_bool('contains_soy'),
                mac_address=_str(data.get('mac_address')) or None,
                hostname=_str(data.get('hostname')) or None,
                assigned_user_id=_int_opt('assigned_user_id'),
                created_by=created_by_id
            )
            loc = _str(data.get('location_code'))
            if loc and not new_stock.location_aisle:
                parts = loc.upper().split('-')
                if len(parts) >= 2:
                    new_stock.location_aisle = parts[0]
                if len(parts) >= 3:
                    new_stock.location_shelf = parts[1]
            new_stock.ensure_public_token()
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

            evt = AssetEvent(
                stock_id=new_stock.id,
                user_id=created_by_id,
                event_type=AssetEventTypeEnum.comprado,
                description='Alta inicial de inventario',
            )
            db.session.add(evt)

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
            'stocks': [s.to_summary_dict() for s in items],
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

    @staticmethod
    def quick_scan(barcode, user_id, tenant_id, mode='lookup', quantity=1):
        """Modo inventario rápido: lookup, increment o decrement."""
        from ..tenant_utils import scope_tenant
        q = scope_tenant(Stock.query.filter(Stock.deleted_at.is_(None)), Stock, tenant_id)
        stock = q.filter_by(barcode=barcode).first()
        if not stock:
            return None, {'error': f'Producto {barcode} no encontrado', 'status': 404}
        if mode in ('increment', 'add'):
            movement = StockMovement(
                stock_id=stock.id, user_id=user_id, quantity=quantity,
                movement_type='entrada', notes='Inventario rápido (+)',
            )
            db.session.add(movement)
        elif mode in ('decrement', 'remove'):
            movement = StockMovement(
                stock_id=stock.id, user_id=user_id, quantity=quantity,
                movement_type='salida', notes='Inventario rápido (-)',
            )
            db.session.add(movement)
        return stock, None