"""Órdenes de compra."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import db
from .utils import role_required
from .services.purchase_order_service import PurchaseOrderService

purchase_orders = Blueprint('purchase_orders', __name__)


@purchase_orders.route('', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_orders():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    return jsonify(PurchaseOrderService.list_orders(page=page, per_page=per_page, status=status)), 200


@purchase_orders.route('/<int:order_id>', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_order(order_id):
    order = PurchaseOrderService.get_order(order_id)
    if not order:
        return jsonify({'error': 'Orden no encontrada'}), 404
    return jsonify(order.to_dict()), 200


@purchase_orders.route('/generate-low-stock', methods=['POST'])
@jwt_required()
@role_required('admin')
def generate_from_low_stock():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    supplier_id = data.get('supplier_id')
    if not supplier_id:
        return jsonify({'error': 'supplier_id es obligatorio'}), 400
    order, err = PurchaseOrderService.generate_from_low_stock(
        supplier_id=int(supplier_id),
        created_by_id=user_id,
        notes=data.get('notes'),
    )
    if err:
        return jsonify({'error': err['error']}), err.get('status', 400)
    db.session.commit()
    return jsonify(order.to_dict()), 201


@purchase_orders.route('', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_order():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    order, err = PurchaseOrderService.create_manual(
        supplier_id=data.get('supplier_id'),
        created_by_id=user_id,
        lines=data.get('lines', []),
        notes=data.get('notes'),
    )
    if err:
        return jsonify({'error': err['error']}), err.get('status', 400)
    db.session.commit()
    return jsonify(order.to_dict()), 201


@purchase_orders.route('/<int:order_id>/approve', methods=['POST'])
@jwt_required()
@role_required('admin')
def approve_order(order_id):
    user_id = int(get_jwt_identity())
    order, err = PurchaseOrderService.approve(order_id, user_id)
    if err:
        return jsonify({'error': err['error']}), err.get('status', 400)
    db.session.commit()
    return jsonify(order.to_dict()), 200


@purchase_orders.route('/<int:order_id>/receive', methods=['POST'])
@jwt_required()
@role_required('admin')
def receive_order(order_id):
    user_id = int(get_jwt_identity())
    order, err = PurchaseOrderService.receive(order_id, user_id)
    if err:
        return jsonify({'error': err['error']}), err.get('status', 400)
    db.session.commit()
    return jsonify(order.to_dict()), 200
