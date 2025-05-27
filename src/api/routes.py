from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from .models import db, Stock, StockMovement, MaintenanceRecord, StockStatusEnum
from datetime import datetime
import boto3
import os

api = Blueprint('api', __name__)
s3 = boto3.client('s3')

@api.route('/stock', methods=['POST'])
@jwt_required()
def create_stock():
    try:
        current_user_id = get_jwt_identity()
        data = request.json

        # Validar código de barras único
        if Stock.query.filter_by(barcode=data['barcode']).first():
            return jsonify({'error': 'El código de barras ya existe'}), 400

        # Procesar imagen si existe
        image_url = None
        if data.get('image'):
            try:
                image_data = data['image'].split(',')[1]  # Remover el prefijo data:image
                filename = f"stock/{data['barcode']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                s3.put_object(
                    Bucket=os.environ.get('S3_BUCKET'),
                    Key=filename,
                    Body=image_data,
                    ContentType='image/jpeg'
                )
                image_url = f"https://{os.environ.get('S3_BUCKET')}.s3.amazonaws.com/{filename}"
            except Exception as e:
                print(f"Error al subir imagen: {str(e)}")

        new_stock = Stock(
            barcode=data['barcode'],
            inventario=data['inventario'],
            dispositivo=data['dispositivo'],
            modelo=data['modelo'],
            descripcion=data.get('descripcion', ''),
            cantidad=data.get('cantidad', 1),
            stocktype=data['stocktype'],
            status=StockStatusEnum.disponible,
            location=data.get('location'),
            serial_number=data.get('serial_number'),
            purchase_date=datetime.strptime(data['purchase_date'], '%Y-%m-%d').date() if data.get('purchase_date') else None,
            warranty_expiry=datetime.strptime(data['warranty_expiry'], '%Y-%m-%d').date() if data.get('warranty_expiry') else None,
            created_by=current_user_id,
            image_url=image_url
        )

        db.session.add(new_stock)
        
        # Registrar movimiento inicial
        movement = StockMovement(
            stock_id=new_stock.id,
            user_id=current_user_id,
            quantity=new_stock.cantidad,
            movement_type='entrada',
            to_location=new_stock.location,
            notes='Registro inicial de inventario'
        )
        db.session.add(movement)
        
        db.session.commit()
        return jsonify({'message': 'Stock creado exitosamente', 'id': new_stock.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

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

        stock_query = Stock.query

        if query:
            stock_query = stock_query.filter(
                or_(
                    Stock.barcode.ilike(f'%{query}%'),
                    Stock.inventario.ilike(f'%{query}%'),
                    Stock.dispositivo.ilike(f'%{query}%'),
                    Stock.modelo.ilike(f'%{query}%'),
                    Stock.descripcion.ilike(f'%{query}%')
                )
            )

        if stocktype:
            stock_query = stock_query.filter(Stock.stocktype == stocktype)
        
        if status:
            stock_query = stock_query.filter(Stock.status == status)
        
        if location:
            stock_query = stock_query.filter(Stock.location == location)

        stocks = stock_query.order_by(Stock.updated_at.desc()).limit(50).all()

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
            } for s in stocks]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

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