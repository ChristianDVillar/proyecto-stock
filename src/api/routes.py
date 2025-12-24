from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, func
from .models import db, Stock, StockMovement, MaintenanceRecord, StockStatusEnum, StockTypeEnum, CustomStockType, DeviceTypeEnum, CustomDeviceType
from .utils import (
    validate_barcode, validate_inventario, validate_modelo, validate_cantidad,
    validate_request_data, error_handler
)
from datetime import datetime
import boto3
import os
from sqlalchemy.orm import Session

api = Blueprint('api', __name__)
s3 = boto3.client('s3')

@api.route('/stock/inventory', methods=['GET'])
@jwt_required()
def get_inventory():
    try:
        # Obtener el inventario agrupado por tipo
        inventory = db.session.query(
            Stock.dispositivo,
            func.count(Stock.id).label('total_items'),
            func.sum(Stock.cantidad).label('total_quantity')
        ).group_by(Stock.dispositivo).all()
        
        # Obtener los tipos personalizados
        custom_types = CustomStockType.query.all()
        custom_types_dict = {t.id: t.name for t in custom_types}
        
        # Formatear la respuesta
        inventory_data = []
        for tipo, items, cantidad in inventory:
            inventory_data.append({
                'tipo': tipo.value if tipo else 'Desconocido',
                'total_items': items,
                'total_cantidad': cantidad
            })
        
        # Obtener el stock detallado
        stock_items = Stock.query.all()
        stock_details = []
        for item in stock_items:
            stock_details.append({
                'id': item.id,
                'barcode': item.barcode,
                'inventario': item.inventario,
                'dispositivo': item.dispositivo.value,
                'modelo': item.modelo,
                'cantidad': item.cantidad,
                'status': item.status.value,
                'location': item.location
            })

        return jsonify({
            'resumen': inventory_data,
            'detalle': stock_details
        }), 200

    except Exception as e:
        print(f"Error al obtener inventario: {str(e)}")
        return jsonify({
            'error': 'Error al obtener el inventario',
            'message': str(e)
        }), 500

@api.route('/stock/types', methods=['GET'])
@jwt_required()
def get_stock_types():
    try:
        # Obtener tipos de stock del enum
        enum_types = [{'id': t.name, 'name': t.value} for t in StockTypeEnum if t.name != 'otro']
        
        # Obtener tipos personalizados de la base de datos
        custom_types = CustomStockType.query.all()
        custom_types_list = [{'id': f'custom_{t.id}', 'name': t.name} for t in custom_types]
        
        # Combinar ambas listas y agregar la opción "otro"
        all_types = enum_types + custom_types_list + [{'id': 'otro', 'name': 'Otro...'}]
        
        return jsonify({
            'types': all_types
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/device/types', methods=['GET'])
@jwt_required()
def get_device_types():
    try:
        # Obtener tipos de dispositivos del enum
        enum_types = [{'id': t.name, 'name': t.value} for t in DeviceTypeEnum]
        
        # Obtener tipos personalizados de la base de datos
        custom_types = CustomDeviceType.query.all()
        custom_types_list = [{'id': t.name, 'name': t.name} for t in custom_types]
        
        # Combinar ambas listas
        all_types = enum_types + custom_types_list
        
        return jsonify({
            'types': all_types
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/stock', methods=['POST'])
@jwt_required()
def create_stock():
    current_user_id = get_jwt_identity()
    
    if current_user_id is None:
        return jsonify({
            'error': 'Usuario no autenticado',
            'message': 'La sesión ha expirado o no es válida. Por favor, inicie sesión nuevamente.'
        }), 401

    data = request.get_json()
    
    # Validar campos requeridos
    required_fields = ['barcode', 'inventario', 'dispositivo', 'modelo']
    is_valid, error_msg = validate_request_data(required_fields, data)
    if not is_valid:
        return jsonify({
            'error': 'Datos inválidos',
            'message': error_msg
        }), 400

    # Validar formato de campos
    barcode_valid, barcode_error = validate_barcode(data['barcode'])
    if not barcode_valid:
        return jsonify({
            'error': 'Código de barras inválido',
            'message': barcode_error
        }), 400

    inventario_valid, inventario_error = validate_inventario(data['inventario'])
    if not inventario_valid:
        return jsonify({
            'error': 'Código de inventario inválido',
            'message': inventario_error
        }), 400

    modelo_valid, modelo_error = validate_modelo(data['modelo'])
    if not modelo_valid:
        return jsonify({
            'error': 'Modelo inválido',
            'message': modelo_error
        }), 400

    # Validar código de barras único
    existing_stock = Stock.query.filter_by(barcode=data['barcode']).first()
    if existing_stock:
        return jsonify({
            'error': 'Código de barras duplicado',
            'message': 'El código de barras ya existe en la base de datos.'
        }), 400

    # Procesar el tipo de dispositivo
    device_type = data.get('dispositivo', '').lower()
    custom_type = None
    device_type_enum = None

    try:
        # Intentar obtener el tipo del enum
        device_type_enum = StockTypeEnum[device_type]
    except KeyError:
        if device_type.startswith('custom_'):
            # Es un tipo personalizado existente
            try:
                custom_type_id = int(device_type.split('_')[1])
                custom_type = CustomStockType.query.get(custom_type_id)
                if not custom_type:
                    return jsonify({
                        'error': 'Tipo personalizado no encontrado',
                        'message': 'El tipo personalizado seleccionado no existe.'
                    }), 400
                device_type_enum = StockTypeEnum.otro
            except (IndexError, ValueError):
                return jsonify({
                    'error': 'Formato de tipo personalizado inválido',
                    'message': 'El formato del tipo personalizado es inválido.'
                }), 400
        else:
            return jsonify({
                'error': 'Tipo de dispositivo inválido',
                'message': f'El tipo de dispositivo "{device_type}" no es válido.',
                'valid_types': [t.name for t in StockTypeEnum]
            }), 400

    # Validar cantidad
    cantidad_valid, cantidad_error = validate_cantidad(data.get('cantidad', 1))
    if not cantidad_valid:
        return jsonify({
            'error': 'Cantidad inválida',
            'message': cantidad_error
        }), 400
    
    cantidad = int(data.get('cantidad', 1))

    # Crear el nuevo stock
    new_stock = Stock(
        barcode=data['barcode'],
        inventario=data['inventario'],
        dispositivo=device_type_enum,
        modelo=data['modelo'],
        descripcion=data.get('descripcion', ''),
        cantidad=cantidad,
        stocktype=device_type_enum,
        status=StockStatusEnum.disponible,
        location=data.get('location', 'default'),
        serial_number=data.get('serial_number'),
        purchase_date=datetime.strptime(data['purchase_date'], '%Y-%m-%d').date() if data.get('purchase_date') else None,
        warranty_expiry=datetime.strptime(data['warranty_expiry'], '%Y-%m-%d').date() if data.get('warranty_expiry') else None,
        created_by=current_user_id
    )

    # Crear el movimiento inicial
    movement = StockMovement(
        user_id=current_user_id,
        quantity=cantidad,
        movement_type='entrada',
        to_location=data.get('location', 'default'),
        notes='Registro inicial de inventario'
    )

    try:
        # Agregar el nuevo stock a la sesión
        db.session.add(new_stock)
        db.session.flush()

        # Asociar el movimiento con el stock
        movement.stock_id = new_stock.id
        db.session.add(movement)
        
        # Confirmar la transacción
        db.session.commit()
        
        response_data = {
            'message': 'Stock creado exitosamente',
            'id': new_stock.id,
            'barcode': new_stock.barcode
        }

        if custom_type:
            response_data['custom_type'] = {
                'id': custom_type.id,
                'name': custom_type.name
            }

        return jsonify(response_data), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error en la transacción: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'error': 'Error al crear el stock',
            'message': str(e)
        }), 500

@api.route('/stock/<barcode>', methods=['GET'])
@jwt_required()
def get_stock(barcode):
    try:
        stock = Stock.query.filter_by(barcode=barcode).first()
        if not stock:
            return jsonify({'error': 'Stock no encontrado'}), 404

        # Incluir últimos movimientos
        movements = StockMovement.query.filter_by(stock_id=stock.id).order_by(StockMovement.timestamp.desc()).limit(5).all()
        
        # Incluir último mantenimiento
        last_maintenance = MaintenanceRecord.query.filter_by(stock_id=stock.id).order_by(MaintenanceRecord.date_performed.desc()).first()

        return jsonify({
            'stock': {
                'id': stock.id,
                'barcode': stock.barcode,
                'inventario': stock.inventario,
                'dispositivo': stock.dispositivo,
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
                'image_url': stock.image_url
            },
            'movements': [{
                'type': m.movement_type,
                'quantity': m.quantity,
                'timestamp': m.timestamp.isoformat(),
                'from_location': m.from_location,
                'to_location': m.to_location,
                'notes': m.notes
            } for m in movements],
            'last_maintenance': {
                'type': last_maintenance.maintenance_type,
                'date': last_maintenance.date_performed.isoformat(),
                'description': last_maintenance.description,
                'status': last_maintenance.status
            } if last_maintenance else None
        }), 200

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
        
        # Paginación
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 100)  # Limitar máximo a 100

        stock_query = Stock.query

        if query:
            stock_query = stock_query.filter(
                or_(
                    Stock.barcode.ilike(f'%{query}%'),
                    Stock.inventario.ilike(f'%{query}%'),
                    Stock.modelo.ilike(f'%{query}%'),
                    Stock.descripcion.ilike(f'%{query}%')
                )
            )

        if stocktype:
            try:
                # Intentar convertir a enum
                if stocktype.startswith('custom_'):
                    custom_id = int(stocktype.split('_')[1])
                    custom_type = CustomStockType.query.get(custom_id)
                    if custom_type:
                        stock_query = stock_query.filter(Stock.stocktype == StockTypeEnum.otro)
                else:
                    stock_type_enum = StockTypeEnum[stocktype]
                    stock_query = stock_query.filter(Stock.stocktype == stock_type_enum)
            except (KeyError, ValueError, IndexError):
                pass  # Ignorar tipos inválidos
        
        if status:
            try:
                status_enum = StockStatusEnum[status]
                stock_query = stock_query.filter(Stock.status == status_enum)
            except KeyError:
                pass  # Ignorar estados inválidos
        
        if location:
            stock_query = stock_query.filter(Stock.location.ilike(f'%{location}%'))

        # Contar total antes de paginar
        total_items = stock_query.count()
        total_pages = (total_items + per_page - 1) // per_page

        # Aplicar paginación
        stocks = stock_query.order_by(Stock.updated_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        ).items

        return jsonify({
            'stocks': [{
                'id': s.id,
                'barcode': s.barcode,
                'inventario': s.inventario,
                'dispositivo': s.dispositivo,
                'modelo': s.modelo,
                'cantidad': s.cantidad,
                'status': s.status.value,
                'location': s.location
            } for s in stocks],
            'total_items': total_items,
            'total_pages': total_pages,
            'current_page': page,
            'per_page': per_page
        }), 200

    except Exception as e:
        print(f"Error in search_stock: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({
            'error': 'Error al buscar stock',
            'message': str(e)
        }), 500

@api.route('/stock/<int:stock_id>/movement', methods=['POST'])
@jwt_required()
def register_movement(stock_id):
    try:
        current_user_id = get_jwt_identity()
        data = request.json

        stock = Stock.query.get(stock_id)
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
        
        # Actualizar ubicación del stock si es necesario
        if data.get('to_location'):
            stock.location = data['to_location']

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

        stock = Stock.query.get(stock_id)
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
        
        # Actualizar información de mantenimiento en el stock
        stock.last_maintenance = maintenance.date_performed
        stock.next_maintenance = maintenance.next_maintenance
        stock.status = StockStatusEnum.mantenimiento if maintenance.status == 'en_proceso' else StockStatusEnum.disponible

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