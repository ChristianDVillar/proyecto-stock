"""Webhooks salientes y autenticación por API key."""
import hashlib
import hmac
import json
import secrets
import urllib.error
import urllib.request
from datetime import datetime
from functools import wraps

from flask import request, jsonify, g

from ..models import db, ApiKey, Webhook
from ..tenant_utils import get_current_tenant_id


def _hash_key(raw_key):
    return hashlib.sha256(raw_key.encode('utf-8')).hexdigest()


class WebhookService:
    @staticmethod
    def list_webhooks(tenant_id=None):
        tid = tenant_id or get_current_tenant_id()
        q = Webhook.query.filter_by(is_active=True)
        if tid:
            q = q.filter_by(tenant_id=tid)
        return [w.to_dict() for w in q.all()]

    @staticmethod
    def create_webhook(tenant_id, url, events=None, secret=None):
        wh = Webhook(
            tenant_id=tenant_id,
            url=url,
            events=events or 'stock.updated,order.approved',
            secret=secret or secrets.token_hex(16),
        )
        db.session.add(wh)
        return wh

    @staticmethod
    def emit(tenant_id, event, payload):
        hooks = Webhook.query.filter_by(tenant_id=tenant_id, is_active=True).all()
        sent = 0
        body = json.dumps({'event': event, 'data': payload, 'timestamp': datetime.utcnow().isoformat()})
        for wh in hooks:
            if event not in (wh.events or '').split(','):
                continue
            headers = {'Content-Type': 'application/json'}
            if wh.secret:
                sig = hmac.new(wh.secret.encode(), body.encode(), hashlib.sha256).hexdigest()
                headers['X-Webhook-Signature'] = sig
            req = urllib.request.Request(wh.url, data=body.encode('utf-8'), headers=headers)
            try:
                urllib.request.urlopen(req, timeout=8)
                sent += 1
            except urllib.error.URLError:
                pass
        return sent


class ApiKeyService:
    @staticmethod
    def list_keys(tenant_id=None):
        tid = tenant_id or get_current_tenant_id()
        q = ApiKey.query.filter_by(is_active=True)
        if tid:
            q = q.filter_by(tenant_id=tid)
        return [k.to_dict() for k in q.all()]

    @staticmethod
    def create_key(tenant_id, name, created_by, scopes='read,write'):
        raw = f'sk_{secrets.token_urlsafe(32)}'
        key = ApiKey(
            tenant_id=tenant_id,
            name=name,
            key_prefix=raw[:12],
            key_hash=_hash_key(raw),
            scopes=scopes,
            created_by=created_by,
        )
        db.session.add(key)
        return key, raw

    @staticmethod
    def validate_key(raw_key):
        if not raw_key or not raw_key.startswith('sk_'):
            return None
        h = _hash_key(raw_key)
        key = ApiKey.query.filter_by(key_hash=h, is_active=True).first()
        if key:
            key.last_used_at = datetime.utcnow()
            return key
        return None


def require_api_key(scope='read'):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            raw = request.headers.get('X-API-Key') or request.headers.get('Authorization', '').replace('Bearer ', '')
            key = ApiKeyService.validate_key(raw)
            if not key:
                return jsonify({'error': 'API key inválida'}), 401
            if scope == 'write' and 'write' not in (key.scopes or ''):
                return jsonify({'error': 'Permiso insuficiente'}), 403
            g.api_key = key
            g.tenant_id = key.tenant_id
            db.session.commit()
            return fn(*args, **kwargs)
        return wrapper
    return decorator
