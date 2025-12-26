"""
Blueprint registration
Centralized route registration with rate limiting
"""
from api.routes import api
from api.auth import auth
from api.users import users


def register_blueprints(app, limiter):
    """Register all blueprints with rate limiting"""
    # Register blueprints
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(auth, url_prefix='/api/auth')
    app.register_blueprint(users, url_prefix='/api/users')
    
    # Apply rate limiting
    limiter.limit("5 per minute")(auth)
    limiter.limit("100 per hour")(api)
    
    # Health check endpoint
    @app.route('/')
    def index():
        from flask import jsonify
        return jsonify({
            'message': 'API funcionando',
            'status': 'healthy'
        })

