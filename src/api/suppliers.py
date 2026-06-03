"""CRUD de proveedores."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from .models import db, Supplier, Stock
from .utils import role_required
from .tenant_utils import get_current_tenant_id, scope_tenant

suppliers = Blueprint('suppliers', __name__)


def _supplier_query():
    return scope_tenant(Supplier.query.filter_by(is_active=True), Supplier)


@suppliers.route('', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_suppliers():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), 100)
    q = request.args.get('q', '').strip()
    query = _supplier_query().order_by(Supplier.name)
    if q:
        query = query.filter(Supplier.name.ilike(f'%{q}%'))
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    items = [s.to_dict() for s in pagination.items]
    return jsonify({
        'items': items,
        'suppliers': items,
        'total': pagination.total,
        'page': page,
        'pages': pagination.pages or 1,
        'per_page': per_page,
    }), 200


@suppliers.route('/<int:supplier_id>', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_supplier(supplier_id):
    s = _supplier_query().filter(Supplier.id == supplier_id).first()
    if not s:
        return jsonify({'error': 'Proveedor no encontrado'}), 404
    data = s.to_dict()
    products = Stock.query.filter_by(supplier_id=supplier_id).filter(Stock.deleted_at.is_(None)).limit(100).all()
    data['products'] = [p.to_summary_dict() for p in products]
    data['product_count'] = Stock.query.filter_by(supplier_id=supplier_id).filter(Stock.deleted_at.is_(None)).count()
    return jsonify(data), 200


@suppliers.route('', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_supplier():
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'El nombre es obligatorio'}), 400
    s = Supplier(
        tenant_id=get_current_tenant_id(),
        name=name,
        tax_id=(data.get('tax_id') or '').strip() or None,
        phone=(data.get('phone') or '').strip() or None,
        email=(data.get('email') or '').strip() or None,
        address=(data.get('address') or '').strip() or None,
        notes=(data.get('notes') or '').strip() or None,
    )
    db.session.add(s)
    db.session.commit()
    return jsonify(s.to_dict()), 201


@suppliers.route('/<int:supplier_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_supplier(supplier_id):
    s = _supplier_query().filter(Supplier.id == supplier_id).first()
    if not s:
        return jsonify({'error': 'Proveedor no encontrado'}), 404
    data = request.get_json() or {}
    for field in ('name', 'tax_id', 'phone', 'email', 'address', 'notes'):
        if field in data:
            val = data[field]
            setattr(s, field, val.strip() if isinstance(val, str) else val)
    if 'is_active' in data:
        s.is_active = bool(data['is_active'])
    db.session.commit()
    return jsonify(s.to_dict()), 200


@suppliers.route('/<int:supplier_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def deactivate_supplier(supplier_id):
    s = _supplier_query().filter(Supplier.id == supplier_id).first()
    if not s:
        return jsonify({'error': 'Proveedor no encontrado'}), 404
    s.is_active = False
    db.session.commit()
    return jsonify({'message': 'Proveedor desactivado'}), 200
