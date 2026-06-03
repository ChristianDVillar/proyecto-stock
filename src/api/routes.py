from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import db, Stock, StockMovement, MaintenanceRecord, StockStatusEnum, StockTypeEnum, CustomStockType, DeviceTypeEnum, CustomDeviceType, AssetEvent, AssetEventTypeEnum
from .repositories.stock_repository import StockRepository
from .utils import (
    validate_barcode, validate_inventario, validate_modelo, validate_cantidad,
    validate_request_data, error_handler, role_required
)
from .services.stock_service import StockService
from datetime import datetime
import os
import json
from urllib import request as urlrequest, error as urlerror

api = Blueprint('api', __name__)


def _format_types_response(enum_cls, custom_model, custom_id_prefix=None, exclude_enum_names=None, extra_items=None):
    """
    Construye respuesta de tipos: enum + custom de BD + ítems extra.
    exclude_enum_names: set de nombres del enum a no incluir (ej. {'otro'}).
    extra_items: lista de dicts [{'id': x, 'name': y}, ...] a añadir al final.
    """
    exclude = exclude_enum_names or set()
    enum_types = [{'id': t.name, 'name': t.value} for t in enum_cls if t.name not in exclude]
    custom_list = custom_model.query.all()
    if custom_id_prefix:
        custom_types_list = [{'id': f'{custom_id_prefix}_{t.id}', 'name': t.name} for t in custom_list]
    else:
        custom_types_list = [{'id': t.name, 'name': t.name} for t in custom_list]
    result = enum_types + custom_types_list
    if extra_items:
        result = result + extra_items
    return {'types': result}


@api.route('/stock/inventory', methods=['GET'])
@jwt_required()
def get_inventory():
    try:
        result = StockService.get_inventory()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': 'Error al obtener el inventario', 'message': str(e)}), 500

@api.route('/stock/types', methods=['GET'])
@jwt_required()
def get_stock_types():
    try:
        return jsonify(_format_types_response(
            StockTypeEnum, CustomStockType,
            custom_id_prefix='custom',
            exclude_enum_names={'otro'},
            extra_items=[{'id': 'otro', 'name': 'Otro...'}]
        )), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/device/types', methods=['GET'])
@jwt_required()
def get_device_types():
    try:
        return jsonify(_format_types_response(DeviceTypeEnum, CustomDeviceType)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/stock', methods=['POST'])
@jwt_required()
def create_stock():
    try:
        current_user_id = get_jwt_identity()
        if current_user_id is None:
            return jsonify({'error': 'Usuario no autenticado', 'message': 'Sesión expirada o no válida.'}), 401
        data = request.get_json()
        try:
            user_id = int(current_user_id)
        except (TypeError, ValueError):
            return jsonify({'error': 'Usuario no autenticado'}), 401
        new_stock, err = StockService.create_stock_item(user_id, data or {})
        if err:
            return jsonify({'error': err['error'], 'message': err.get('message', '')}), err.get('status', 500)
        db.session.commit()
        response_data = {'message': 'Stock creado exitosamente', 'id': new_stock.id, 'barcode': new_stock.barcode}
        return jsonify(response_data), 201
    except Exception as e:
        current_app.logger.exception('create_stock failed')
        msg = str(e) or type(e).__name__
        return jsonify({'error': 'Error al crear el stock', 'message': msg}), 500

@api.route('/stock/<barcode>', methods=['GET'])
@jwt_required()
def get_stock(barcode):
    try:
        stock = StockRepository.get_by_barcode(barcode, include_deleted=False)
        if not stock:
            return jsonify({'error': 'Stock no encontrado'}), 404

        movements = StockMovement.query.filter_by(stock_id=stock.id).order_by(StockMovement.timestamp.desc()).limit(5).all()
        last_maintenance = MaintenanceRecord.query.filter_by(stock_id=stock.id).order_by(MaintenanceRecord.date_performed.desc()).first()

        return jsonify(StockService.format_stock_detail(stock, movements, last_maintenance)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/stock/search', methods=['GET'])
@jwt_required()
def search_stock():
    try:
        query = request.args.get('q', '')
        stocktype = request.args.get('type')
        status = request.args.get('status')
        location = request.args.get('location')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        result = StockService.search_stock(query=query, stocktype=stocktype, status=status, location=location, page=page, per_page=per_page)
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.exception('stock/search failed')
        return jsonify({'error': 'Error al buscar stock', 'message': str(e)}), 500


@api.route('/stock/search_es', methods=['GET'])
@jwt_required()
def search_stock_elasticsearch():
    """
    Búsqueda avanzada de stock usando Elasticsearch.
    Requiere que ELASTICSEARCH_URL (y opcionalmente ELASTICSEARCH_INDEX) estén configurados.
    """
    q = (request.args.get('q') or '').strip()
    if not q:
        return jsonify({'error': 'Parámetro q requerido'}), 400

    es_url = current_app.config.get('ELASTICSEARCH_URL') or os.environ.get('ELASTICSEARCH_URL', 'http://elasticsearch:9200')
    index = current_app.config.get('ELASTICSEARCH_INDEX', 'stock')
    search_url = f"{es_url.rstrip('/')}/{index}/_search"

    body = {
        "query": {
            "multi_match": {
                "query": q,
                "fields": ["barcode^3", "inventario^3", "modelo", "descripcion"]
            }
        },
        "size": int(request.args.get('size', 25) or 25)
    }

    try:
        data = json.dumps(body).encode("utf-8")
        req = urlrequest.Request(
            search_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="GET" if current_app.config.get("ELASTICSEARCH_ALLOW_GET_BODY", True) else "POST",
        )
        with urlrequest.urlopen(req, timeout=3) as resp:
            payload = json.loads(resp.read().decode("utf-8") or "{}")
    except urlerror.HTTPError as e:
        msg = e.read().decode("utf-8") if hasattr(e, "read") else str(e)
        current_app.logger.exception("elasticsearch search HTTPError")
        return jsonify({"error": "Error al buscar en Elasticsearch", "message": msg}), 502
    except Exception as e:
        current_app.logger.exception("elasticsearch search failed")
        return jsonify({"error": "No se pudo conectar a Elasticsearch", "message": str(e)}), 502

    hits = (payload.get("hits") or {}).get("hits") or []
    total_info = (payload.get("hits") or {}).get("total") or {}
    total = total_info.get("value", len(hits)) if isinstance(total_info, dict) else total_info

    results = []
    for h in hits:
        src = h.get("_source") or {}
        results.append({
            "id": src.get("id") or h.get("_id"),
            "score": h.get("_score"),
            "barcode": src.get("barcode"),
            "inventario": src.get("inventario"),
            "modelo": src.get("modelo"),
            "descripcion": src.get("descripcion"),
            "location": src.get("location"),
            "raw": src,
        })

    return jsonify({"query": q, "total": total, "results": results}), 200


@api.route('/stock/<int:stock_id>', methods=['PATCH'])
@jwt_required()
@role_required('admin')
def update_stock(stock_id):
    """Actualiza campos comerciales / activo IT del stock."""
    try:
        stock = StockRepository.get_by_id(stock_id, include_deleted=False)
        if not stock:
            return jsonify({'error': 'Stock no encontrado'}), 404
        data = request.get_json() or {}
        updatable = (
            'minimum_stock', 'optimal_stock', 'unit_cost', 'supplier_id',
            'expiration_date', 'batch_number', 'serial_number', 'mac_address',
            'hostname', 'assigned_user_id', 'location', 'descripcion',
            'contains_gluten', 'contains_milk', 'contains_nuts', 'contains_soy',
            'warranty_expiry', 'purchase_date',
        )
        for key in updatable:
            if key not in data:
                continue
            val = data[key]
            if key in ('expiration_date', 'warranty_expiry', 'purchase_date') and val:
                try:
                    val = datetime.strptime(val, '%Y-%m-%d').date()
                except ValueError:
                    continue
            if key in ('minimum_stock', 'optimal_stock', 'supplier_id', 'assigned_user_id') and val is not None:
                try:
                    val = int(val)
                except (TypeError, ValueError):
                    continue
            if key == 'unit_cost' and val is not None:
                try:
                    val = float(val)
                except (TypeError, ValueError):
                    continue
            setattr(stock, key, val)
        if 'assigned_user_id' in data and data['assigned_user_id']:
            evt = AssetEvent(
                stock_id=stock.id,
                user_id=int(get_jwt_identity()),
                event_type=AssetEventTypeEnum.asignado,
                description=f'Asignado a usuario ID {data["assigned_user_id"]}',
            )
            db.session.add(evt)
        db.session.commit()
        return jsonify(stock.to_summary_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api.route('/stock/<int:stock_id>/asset-history', methods=['GET'])
@jwt_required()
@role_required('admin')
def asset_history(stock_id):
    stock = StockRepository.get_by_id(stock_id, include_deleted=False)
    if not stock:
        return jsonify({'error': 'Stock no encontrado'}), 404
    events = AssetEvent.query.filter_by(stock_id=stock_id).order_by(AssetEvent.created_at.desc()).all()
    movements = StockMovement.query.filter_by(stock_id=stock_id).order_by(StockMovement.timestamp.desc()).limit(50).all()
    maintenance = MaintenanceRecord.query.filter_by(stock_id=stock_id).order_by(MaintenanceRecord.date_performed.desc()).limit(20).all()
    return jsonify({
        'stock': stock.to_summary_dict(),
        'asset_events': [e.to_dict() for e in events],
        'movements': [{'type': m.movement_type, 'quantity': m.quantity, 'timestamp': m.timestamp.isoformat(), 'notes': m.notes} for m in movements],
        'maintenance': [{'type': m.maintenance_type, 'date': m.date_performed.isoformat(), 'status': m.status} for m in maintenance],
    }), 200


@api.route('/stock/<int:stock_id>', methods=['DELETE'])
@jwt_required()
def delete_stock(stock_id):
    """Soft delete: marca deleted_at y registra en stock_history."""
    try:
        current_user_id = get_jwt_identity()
        if current_user_id is None:
            return jsonify({'error': 'Usuario no autenticado'}), 401
        user_id = int(current_user_id)
        stock, err = StockService.soft_delete_stock(stock_id, user_id)
        if err:
            return jsonify({'error': err['error'], 'message': err.get('message', '')}), err.get('status', 500)
        db.session.commit()
        return jsonify({'message': 'Stock eliminado (soft delete)'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/stock/<int:stock_id>/movement', methods=['POST'])
@jwt_required()
def register_movement(stock_id):
    try:
        current_user_id = get_jwt_identity()
        data = request.json

        stock = StockRepository.get_by_id(stock_id, include_deleted=False)
        if not stock:
            return jsonify({'error': 'Stock no encontrado'}), 404

        # Validar cantidad disponible para salidas
        if data['movement_type'] == 'salida' and stock.cantidad < data['quantity']:
            return jsonify({'error': 'Cantidad insuficiente en stock'}), 400

        movement = StockMovement(
            stock_id=stock_id,
            user_id=current_user_id,
            quantity=data['quantity'],
            movement_type=data['movement_type'],
            from_location=data.get('from_location', stock.location),
            to_location=data.get('to_location'),
            notes=data.get('notes')
        )
        db.session.add(movement)

        new_location = data.get('to_location') or stock.location
        current_version = getattr(stock, 'version', 1)
        rows = db.session.query(Stock).filter(
            Stock.id == stock_id,
            Stock.version == current_version
        ).update({
            Stock.location: new_location,
            Stock.version: current_version + 1,
            Stock.updated_at: datetime.utcnow()
        }, synchronize_session=False)
        if rows == 0:
            db.session.rollback()
            return jsonify({'error': 'El stock fue modificado por otro usuario', 'code': 'conflict'}), 409
        db.session.commit()
        return jsonify({'message': 'Movimiento registrado exitosamente'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/stock/<int:stock_id>/maintenance', methods=['POST'])
@jwt_required()
def register_maintenance(stock_id):
    try:
        current_user_id = get_jwt_identity()
        data = request.json

        stock = StockRepository.get_by_id(stock_id, include_deleted=False)
        if not stock:
            return jsonify({'error': 'Stock no encontrado'}), 404

        maintenance = MaintenanceRecord(
            stock_id=stock_id,
            technician_id=current_user_id,
            maintenance_type=data['maintenance_type'],
            description=data['description'],
            cost=data.get('cost'),
            next_maintenance=datetime.strptime(data['next_maintenance'], '%Y-%m-%d') if data.get('next_maintenance') else None,
            status=data['status']
        )

        db.session.add(maintenance)
        next_maint = maintenance.next_maintenance
        new_status = StockStatusEnum.mantenimiento if maintenance.status == 'en_proceso' else StockStatusEnum.disponible
        current_version = getattr(stock, 'version', 1)
        rows = db.session.query(Stock).filter(
            Stock.id == stock_id,
            Stock.version == current_version
        ).update({
            Stock.last_maintenance: maintenance.date_performed,
            Stock.next_maintenance: next_maint,
            Stock.status: new_status,
            Stock.version: current_version + 1,
            Stock.updated_at: datetime.utcnow()
        }, synchronize_session=False)
        if rows == 0:
            db.session.rollback()
            return jsonify({'error': 'El stock fue modificado por otro usuario', 'code': 'conflict'}), 409
        db.session.commit()
        return jsonify({'message': 'Mantenimiento registrado exitosamente'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api.route('/stock/types', methods=['POST'])
@jwt_required()
def add_stock_type():
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({
                'error': 'Datos inválidos',
                'message': 'Debe proporcionar un nombre para el nuevo tipo'
            }), 400
            
        new_type_name = data['name'].lower()
        
        # Verificar si ya existe
        existing_type = CustomStockType.query.filter_by(name=new_type_name).first()
        if existing_type:
            return jsonify({
                'error': 'Tipo duplicado',
                'message': 'Este tipo ya existe en la base de datos'
            }), 400
            
        # Crear nuevo tipo
        new_type = CustomStockType(
            name=new_type_name,
            created_by=current_user_id
        )
        
        db.session.add(new_type)
        db.session.commit()
        
        return jsonify({
            'message': 'Tipo creado exitosamente',
            'type': {
                'id': f'custom_{new_type.id}',
                'name': new_type.name
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Error al crear el tipo',
            'message': str(e)
        }), 500 