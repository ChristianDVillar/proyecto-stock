"""Multi-almacén: CRUD y listado."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from .models import db, Warehouse, Stock
from .utils import role_required
from .tenant_utils import get_current_tenant_id, scope_tenant

warehouses = Blueprint('warehouses', __name__)


@warehouses.route('', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_warehouses():
    tid = get_current_tenant_id()
    q = scope_tenant(Warehouse.query.filter_by(is_active=True), Warehouse, tid)
    items = [w.to_dict() for w in q.order_by(Warehouse.name).all()]
    return jsonify({'items': items, 'warehouses': items}), 200


@warehouses.route('', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_warehouse():
    tid = get_current_tenant_id()
    if not tid:
        return jsonify({'error': 'Sin tenant asignado'}), 400
    data = request.get_json() or {}
    code = (data.get('code') or '').strip().upper()
    name = (data.get('name') or '').strip()
    if not code or not name:
        return jsonify({'error': 'code y name son obligatorios'}), 400
    if Warehouse.query.filter_by(tenant_id=tid, code=code).first():
        return jsonify({'error': 'Código de almacén duplicado'}), 400
    wh = Warehouse(
        tenant_id=tid,
        code=code,
        name=name,
        city=(data.get('city') or '').strip() or None,
        address=(data.get('address') or '').strip() or None,
        is_default=bool(data.get('is_default')),
    )
    if wh.is_default:
        Warehouse.query.filter_by(tenant_id=tid).update({'is_default': False})
    db.session.add(wh)
    db.session.commit()
    return jsonify(wh.to_dict()), 201


@warehouses.route('/<int:wh_id>/stock', methods=['GET'])
@jwt_required()
@role_required('admin')
def warehouse_stock(wh_id):
    tid = get_current_tenant_id()
    wh = Warehouse.query.filter_by(id=wh_id, tenant_id=tid).first()
    if not wh:
        return jsonify({'error': 'Almacén no encontrado'}), 404
    stocks = Stock.query.filter_by(warehouse_id=wh_id, tenant_id=tid).filter(
        Stock.deleted_at.is_(None)
    ).all()
    return jsonify({
        'warehouse': wh.to_dict(),
        'items': [s.to_summary_dict() for s in stocks],
        'total': len(stocks),
    }), 200
