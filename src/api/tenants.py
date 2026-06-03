"""Multi-tenant: gestión de empresas (SaaS)."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from .models import db, Tenant, TenantPlanEnum, User
from .utils import role_required
from .tenant_utils import ensure_default_tenant, get_current_user

tenants = Blueprint('tenants', __name__)


@tenants.route('', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_tenants():
    user = get_current_user()
    # Admin de plataforma ve todos; admin de tenant solo el suyo
    if user and user.tenant_id:
        t = Tenant.query.get(user.tenant_id)
        items = [t.to_dict()] if t else []
    else:
        items = [t.to_dict() for t in Tenant.query.filter_by(is_active=True).all()]
    return jsonify({'items': items, 'tenants': items}), 200


@tenants.route('', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_tenant():
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    slug = (data.get('slug') or '').strip().lower().replace(' ', '-')
    if not name or not slug:
        return jsonify({'error': 'name y slug son obligatorios'}), 400
    if Tenant.query.filter_by(slug=slug).first():
        return jsonify({'error': 'El slug ya existe'}), 400
    plan = data.get('plan', 'starter')
    try:
        plan_enum = TenantPlanEnum[plan]
    except KeyError:
        plan_enum = TenantPlanEnum.starter
    t = Tenant(name=name, slug=slug, plan=plan_enum, is_active=True)
    db.session.add(t)
    db.session.commit()
    return jsonify(t.to_dict()), 201


@tenants.route('/current', methods=['GET'])
@jwt_required()
def current_tenant():
    user = get_current_user()
    if not user or not user.tenant_id:
        tenant, wh = ensure_default_tenant()
        if user and not user.tenant_id:
            user.tenant_id = tenant.id
            db.session.commit()
        return jsonify({**tenant.to_dict(), 'default_warehouse_id': wh.id}), 200
    t = Tenant.query.get(user.tenant_id)
    if not t:
        return jsonify({'error': 'Tenant no encontrado'}), 404
    return jsonify(t.to_dict()), 200
