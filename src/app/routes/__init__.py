"""
Register all blueprints
"""
from app.routes import stock, auth, users


def register_blueprints(app):
    """Register all application blueprints"""
    from app.routes.stock import stock_bp
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    
    app.register_blueprint(stock_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    
    # Health check endpoint
    @app.route('/')
    def index():
        return {'message': 'API funcionando correctamente', 'status': 'ok'}

