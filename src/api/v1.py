"""API pública v1 (autenticación por API key)."""
from flask import Blueprint, request, jsonify, g
from .models import db, Stock, StockMovement
from .services.webhook_service import require_api_key, WebhookService

v1 = Blueprint('v1', __name__)


@v1.route('/stock', methods=['GET'])
@require_api_key('read')
def v1_list_stock():
    barcode = request.args.get('barcode')
    q = Stock.query.filter_by(tenant_id=g.tenant_id).filter(Stock.deleted_at.is_(None))
    if barcode:
        item = q.filter_by(barcode=barcode).first()
        if not item:
            return jsonify({'error': 'No encontrado'}), 404
        return jsonify(item.to_summary_dict()), 200
    items = q.limit(min(int(request.args.get('limit', 50)), 200)).all()
    return jsonify({'items': [s.to_summary_dict() for s in items]}), 200


@v1.route('/stock/<barcode>/movement', methods=['POST'])
@require_api_key('write')
def v1_stock_movement(barcode):
    stock = Stock.query.filter_by(
        tenant_id=g.tenant_id, barcode=barcode
    ).filter(Stock.deleted_at.is_(None)).first()
    if not stock:
        return jsonify({'error': 'Stock no encontrado'}), 404
    data = request.get_json() or {}
    qty = int(data.get('quantity', 0))
    mtype = data.get('movement_type', 'salida')
    if qty <= 0:
        return jsonify({'error': 'quantity debe ser > 0'}), 400
    if mtype not in ('entrada', 'salida'):
        return jsonify({'error': 'movement_type debe ser entrada o salida'}), 400
    movement = StockMovement(
        stock_id=stock.id,
        user_id=g.api_key.created_by or 1,
        quantity=qty,
        movement_type=mtype,
        notes=data.get('notes') or 'API v1',
    )
    db.session.add(movement)
    db.session.commit()
    WebhookService.emit(g.tenant_id, 'stock.updated', {
        'barcode': barcode,
        'movement_type': mtype,
        'quantity': qty,
        'new_quantity': stock.cantidad,
    })
    return jsonify({'message': 'Movimiento registrado', 'stock': stock.to_summary_dict()}), 201
