"""Portal de cliente: consultas limitadas sin panel admin."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import Stock, ItemRequest, PurchaseOrder, User
from .tenant_utils import get_current_tenant_id, scope_tenant
from .services.purchase_order_service import PurchaseOrderService

portal = Blueprint('portal', __name__)


def _portal_user():
    user = User.query.get(int(get_jwt_identity()))
    if not user or not user.is_active:
        return None
    if user.user_type.value == 'admin':
        return None  # admins usan panel principal
    return user


@portal.route('/stock', methods=['GET'])
@jwt_required()
def portal_stock():
    user = _portal_user()
    if not user:
        return jsonify({'error': 'Acceso portal no autorizado'}), 403
    tid = user.tenant_id
    q = scope_tenant(Stock.query.filter(Stock.deleted_at.is_(None)), Stock, tid)
    search = request.args.get('q', '').strip()
    if search:
        q = q.filter(
            (Stock.modelo.ilike(f'%{search}%')) | (Stock.barcode.ilike(f'%{search}%'))
        )
    items = q.limit(100).all()
    return jsonify({'items': [s.to_summary_dict() for s in items]}), 200


@portal.route('/solicitudes', methods=['GET'])
@jwt_required()
def portal_solicitudes():
    user = _portal_user()
    if not user:
        return jsonify({'error': 'Acceso portal no autorizado'}), 403
    reqs = ItemRequest.query.filter_by(user_id=user.id).order_by(
        ItemRequest.created_at.desc()
    ).limit(50).all()
    from .solicitudes import _serialize_solicitud
    return jsonify({'items': [_serialize_solicitud(r) for r in reqs]}), 200


@portal.route('/orders', methods=['GET'])
@jwt_required()
def portal_orders():
    user = _portal_user()
    if not user:
        return jsonify({'error': 'Acceso portal no autorizado'}), 403
    data = PurchaseOrderService.list_orders(page=1, per_page=20)
    return jsonify(data), 200


@portal.route('/summary', methods=['GET'])
@jwt_required()
def portal_summary():
    user = _portal_user()
    if not user:
        return jsonify({'error': 'Acceso portal no autorizado'}), 403
    tid = user.tenant_id
    stock_count = scope_tenant(
        Stock.query.filter(Stock.deleted_at.is_(None)), Stock, tid
    ).count()
    pending = ItemRequest.query.filter_by(user_id=user.id, status='pendiente').count()
    return jsonify({
        'username': user.username,
        'tenant_id': tid,
        'stock_items': stock_count,
        'pending_requests': pending,
    }), 200
