"""
Blueprint registration
Centralized route registration with rate limiting
"""
from flask import jsonify
from sqlalchemy import text

from api.models import db
from api.routes import api
from api.auth import auth
from api.users import users
from api.solicitudes import solicitudes


def register_blueprints(app, limiter):
    """Register all blueprints with rate limiting"""
    # Register blueprints
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(auth, url_prefix='/api/auth')
    app.register_blueprint(users, url_prefix='/api/users')
    app.register_blueprint(solicitudes, url_prefix='/api/solicitudes')
    
    # Apply rate limiting
    limiter.limit("5 per minute")(auth)
    limiter.limit("100 per hour")(api)

    # Health: ping ligero
    @app.route('/')
    def index():
        return jsonify({'message': 'API funcionando', 'status': 'healthy'})

    @app.route('/health')
    def health():
        """Ping básico: solo DB. Útil para load balancers."""
        status = {'status': 'healthy', 'checks': {}}
        try:
            db.session.execute(text('SELECT 1'))
            status['checks']['database'] = 'ok'
        except Exception as e:
            status['status'] = 'unhealthy'
            status['checks']['database'] = str(e)
        code = 200 if status['status'] == 'healthy' else 503
        return jsonify(status), code

    @app.route('/ready')
    def ready():
        """Readiness: DB + Redis (si RATELIMIT_STORAGE_URL). Para K8s/orquestación."""
        status = {'status': 'healthy', 'checks': {}}
        try:
            db.session.execute(text('SELECT 1'))
            status['checks']['database'] = 'ok'
        except Exception as e:
            status['status'] = 'unhealthy'
            status['checks']['database'] = str(e)
        redis_url = app.config.get('RATELIMIT_STORAGE_URL') or ''
        if redis_url.startswith('redis://'):
            try:
                import redis
                r = redis.from_url(redis_url)
                r.ping()
                status['checks']['redis'] = 'ok'
            except Exception as e:
                status['checks']['redis'] = str(e)
                status['status'] = 'unhealthy'
        code = 200 if status['status'] == 'healthy' else 503
        return jsonify(status), code

