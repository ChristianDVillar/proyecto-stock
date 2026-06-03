"""Configuración y disparo de alertas."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from .models import db
from .utils import role_required
from .tenant_utils import get_current_tenant_id
from .services.alert_service import AlertService

alerts = Blueprint('alerts', __name__)


@alerts.route('', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_alerts():
    return jsonify({'configs': AlertService.list_configs()}), 200


@alerts.route('', methods=['PUT'])
@jwt_required()
@role_required('admin')
def upsert_alert():
    tid = get_current_tenant_id()
    if not tid:
        return jsonify({'error': 'Sin tenant'}), 400
    data = request.get_json() or {}
    cfg, err = AlertService.upsert_config(
        tenant_id=tid,
        channel=data.get('channel'),
        event_type=data.get('event_type'),
        enabled=data.get('enabled', True),
        destination=data.get('destination'),
        extra_config=data.get('extra_config'),
    )
    if err:
        return jsonify({'error': err['error']}), err.get('status', 400)
    db.session.commit()
    return jsonify(cfg.to_dict()), 200


@alerts.route('/check', methods=['POST'])
@jwt_required()
@role_required('admin')
def check_alerts():
    return jsonify(AlertService.check_stock_alerts()), 200


@alerts.route('/test', methods=['POST'])
@jwt_required()
@role_required('admin')
def test_alert():
    tid = get_current_tenant_id()
    data = request.get_json() or {}
    event = data.get('event_type', 'low_stock')
    result = AlertService.dispatch(tid, event, data.get('message', 'Alerta de prueba — Control Stock'))
    return jsonify(result), 200
