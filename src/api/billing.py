"""Facturación SaaS: planes y uso."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from .models import db, Tenant, TenantPlanEnum
from .utils import role_required
from .tenant_utils import get_current_tenant_id
from .services.billing_service import BillingService

billing = Blueprint('billing', __name__)


@billing.route('/plans', methods=['GET'])
@jwt_required()
def list_plans():
    return jsonify({'plans': BillingService.get_plans()}), 200


@billing.route('/usage', methods=['GET'])
@jwt_required()
@role_required('admin')
def tenant_usage():
    usage = BillingService.get_tenant_usage()
    if not usage:
        return jsonify({'error': 'Tenant no encontrado'}), 404
    return jsonify(usage), 200


@billing.route('/plan', methods=['PATCH'])
@jwt_required()
@role_required('admin')
def change_plan():
    tid = get_current_tenant_id()
    tenant = Tenant.query.get(tid)
    if not tenant:
        return jsonify({'error': 'Tenant no encontrado'}), 404
    plan_name = (request.get_json() or {}).get('plan', '').strip()
    try:
        tenant.plan = TenantPlanEnum[plan_name]
    except KeyError:
        return jsonify({'error': 'Plan inválido (starter, pro, business, enterprise)'}), 400
    db.session.commit()
    return jsonify(BillingService.get_tenant_usage(tid)), 200
