"""Alertas automáticas: Email, Telegram, Discord."""
import json
import smtplib
import ssl
import urllib.error
import urllib.request
from email.mime.text import MIMEText

from flask import current_app

from ..models import (
    db, AlertConfig, AlertChannelEnum, AlertEventEnum, Stock,
)
from ..tenant_utils import get_current_tenant_id, scope_tenant


class AlertService:
    @staticmethod
    def list_configs(tenant_id=None):
        tid = tenant_id or get_current_tenant_id()
        q = AlertConfig.query
        if tid:
            q = q.filter_by(tenant_id=tid)
        return [c.to_dict() for c in q.all()]

    @staticmethod
    def upsert_config(tenant_id, channel, event_type, enabled=True, destination=None, extra_config=None):
        try:
            ch = AlertChannelEnum[channel]
            ev = AlertEventEnum[event_type]
        except KeyError:
            return None, {'error': 'Canal o evento inválido', 'status': 400}
        cfg = AlertConfig.query.filter_by(
            tenant_id=tenant_id, channel=ch, event_type=ev
        ).first()
        if not cfg:
            cfg = AlertConfig(tenant_id=tenant_id, channel=ch, event_type=ev)
            db.session.add(cfg)
        cfg.enabled = enabled
        cfg.destination = destination
        cfg.extra_config = json.dumps(extra_config) if extra_config else None
        return cfg, None

    @staticmethod
    def _send_email(to_addr, subject, body):
        host = current_app.config.get('SMTP_HOST')
        port = current_app.config.get('SMTP_PORT', 587)
        user = current_app.config.get('SMTP_USER')
        password = current_app.config.get('SMTP_PASSWORD')
        from_addr = current_app.config.get('SMTP_FROM', user)
        if not host or not to_addr:
            current_app.logger.info('Alert email skipped (SMTP not configured): %s', subject)
            return False
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = subject
        msg['From'] = from_addr
        msg['To'] = to_addr
        try:
            with smtplib.SMTP(host, port) as server:
                server.starttls(context=ssl.create_default_context())
                if user and password:
                    server.login(user, password)
                server.sendmail(from_addr, [to_addr], msg.as_string())
            return True
        except Exception as e:
            current_app.logger.warning('Alert email failed: %s', e)
            return False

    @staticmethod
    def _send_telegram(bot_token, chat_id, text):
        if not bot_token or not chat_id:
            return False
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        payload = json.dumps({'chat_id': chat_id, 'text': text}).encode('utf-8')
        req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
        try:
            urllib.request.urlopen(req, timeout=10)
            return True
        except urllib.error.URLError as e:
            current_app.logger.warning('Telegram alert failed: %s', e)
            return False

    @staticmethod
    def _send_discord(webhook_url, content):
        if not webhook_url:
            return False
        payload = json.dumps({'content': content}).encode('utf-8')
        req = urllib.request.Request(
            webhook_url, data=payload, headers={'Content-Type': 'application/json'}
        )
        try:
            urllib.request.urlopen(req, timeout=10)
            return True
        except urllib.error.URLError as e:
            current_app.logger.warning('Discord alert failed: %s', e)
            return False

    @staticmethod
    def dispatch(tenant_id, event_type, message):
        try:
            ev = AlertEventEnum[event_type]
        except KeyError:
            return {'sent': 0}
        configs = AlertConfig.query.filter_by(
            tenant_id=tenant_id, event_type=ev, enabled=True
        ).all()
        sent = 0
        for cfg in configs:
            extra = json.loads(cfg.extra_config) if cfg.extra_config else {}
            if cfg.channel == AlertChannelEnum.email:
                if AlertService._send_email(cfg.destination, f'[Stock] {event_type}', message):
                    sent += 1
            elif cfg.channel == AlertChannelEnum.telegram:
                token = extra.get('bot_token') or current_app.config.get('TELEGRAM_BOT_TOKEN')
                if AlertService._send_telegram(token, cfg.destination, message):
                    sent += 1
            elif cfg.channel == AlertChannelEnum.discord:
                url = cfg.destination or current_app.config.get('DISCORD_WEBHOOK_URL')
                if AlertService._send_discord(url, message):
                    sent += 1
        return {'sent': sent}

    @staticmethod
    def check_stock_alerts(tenant_id=None):
        tid = tenant_id or get_current_tenant_id()
        q = scope_tenant(Stock.query.filter(Stock.deleted_at.is_(None)), Stock, tid)
        critical = []
        low = []
        for s in q.all():
            level = s.stock_level()
            label = f'{s.modelo} ({s.barcode}) x{s.cantidad}'
            if level == 'critico':
                critical.append(label)
            elif level == 'bajo':
                low.append(label)
        results = []
        if critical:
            msg = 'Stock CRÍTICO:\n' + '\n'.join(critical[:20])
            results.append(AlertService.dispatch(tid, 'critical_stock', msg))
        if low:
            msg = 'Stock bajo:\n' + '\n'.join(low[:20])
            results.append(AlertService.dispatch(tid, 'low_stock', msg))
        return {'critical_count': len(critical), 'low_count': len(low), 'dispatches': results}

    @staticmethod
    def notify_order_approved(tenant_id, order_number):
        msg = f'Orden de compra aprobada: {order_number}'
        return AlertService.dispatch(tenant_id, 'order_approved', msg)
