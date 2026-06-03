"""API keys y webhooks."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import db
from .utils import role_required
from .tenant_utils import get_current_tenant_id
from .services.webhook_service import ApiKeyService, WebhookService

integrations = Blueprint('integrations', __name__)


@integrations.route('/api-keys', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_api_keys():
    return jsonify({'api_keys': ApiKeyService.list_keys()}), 200


@integrations.route('/api-keys', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_api_key():
    tid = get_current_tenant_id()
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'name es obligatorio'}), 400
    key, raw = ApiKeyService.create_key(
        tenant_id=tid,
        name=name,
        created_by=int(get_jwt_identity()),
        scopes=data.get('scopes', 'read,write'),
    )
    db.session.commit()
    result = key.to_dict()
    result['key'] = raw  # solo se muestra una vez
    return jsonify(result), 201


@integrations.route('/webhooks', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_webhooks():
    return jsonify({'webhooks': WebhookService.list_webhooks()}), 200


@integrations.route('/webhooks', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_webhook():
    tid = get_current_tenant_id()
    data = request.get_json() or {}
    url = (data.get('url') or '').strip()
    if not url:
        return jsonify({'error': 'url es obligatoria'}), 400
    wh = WebhookService.create_webhook(tid, url, data.get('events'))
    db.session.commit()
    result = wh.to_dict()
    result['secret'] = wh.secret
    return jsonify(result), 201
