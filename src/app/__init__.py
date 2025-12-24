"""
Application Factory Pattern
Creates and configures the Flask application
"""
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
# from flask_migrate import Migrate  # Temporalmente deshabilitado por compatibilidad Python 3.13
from flask_admin import Admin
from flask_login import LoginManager
from flasgger import Swagger
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from .config import Config
from .models import db
from .extensions import jwt, limiter, login_manager, admin
from .routes import register_blueprints
from .errors import register_error_handlers


def create_app(config_name='development'):
    """
    Application factory pattern
    Creates Flask app instance with configuration
    """
    app = Flask(__name__)
    
    # Load configuration
    config_class = Config.get_config(config_name)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    # Migrate(app, db)  # Temporalmente deshabilitado
    
    # Setup CORS
    CORS(app, 
         resources={r"/*": {
             "origins": config_class.CORS_ORIGINS,
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization", "Accept", "X-Requested-With"],
             "expose_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True,
             "max_age": 3600
         }},
         supports_credentials=True)
    
    # Initialize JWT
    jwt.init_app(app)
    setup_jwt_callbacks(jwt)
    
    # Initialize rate limiter
    limiter.init_app(app)
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    setup_login_manager(login_manager)
    
    # Initialize Flask-Admin
    admin.init_app(app)
    setup_admin(admin, app)
    
    # Setup Swagger
    setup_swagger(app)
    
    # Register blueprints
    register_blueprints(app, limiter)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Setup database
    with app.app_context():
        db.create_all()
        from .models import User, UserTypeEnum
        from werkzeug.security import generate_password_hash
        init_default_admin()
    
    return app


def setup_jwt_callbacks(jwt_manager):
    """Configure JWT callbacks"""
    from .models import User
    
    @jwt_manager.user_identity_loader
    def user_identity_lookup(user):
        if isinstance(user, dict):
            return str(user.get('id'))
        return str(user) if user is not None else None
    
    @jwt_manager.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        try:
            identity = jwt_data["sub"]
            user_id = int(identity)
            return User.query.filter_by(id=user_id).one_or_none()
        except (ValueError, KeyError):
            return None
    
    @jwt_manager.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        try:
            if not isinstance(jwt_payload.get('sub'), str):
                return True
            return False
        except Exception:
            return True
    
    @jwt_manager.invalid_token_loader
    def invalid_token_callback(error_string):
        from flask import jsonify
        return jsonify({
            'error': 'Token inválido',
            'message': f'El token no es válido: {error_string}'
        }), 401
    
    @jwt_manager.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        from flask import jsonify
        return jsonify({
            'error': 'Token expirado',
            'message': 'El token ha expirado. Por favor, inicie sesión nuevamente.'
        }), 401
    
    @jwt_manager.unauthorized_loader
    def unauthorized_callback(error_string):
        from flask import jsonify
        return jsonify({
            'error': 'Token no proporcionado',
            'message': f'No se proporcionó un token válido: {error_string}'
        }), 401


def setup_login_manager(login_mgr):
    """Configure Flask-Login"""
    from .models import User
    
    @login_mgr.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    login_mgr.login_view = 'auth.login'


def setup_admin(admin_instance, app):
    """Configure Flask-Admin"""
    from flask_admin.contrib.sqla import ModelView
    from flask import redirect, url_for, request
    from flask_login import current_user
    from .models import User, Stock, Form, DetailForm, UserUUID, UserTypeEnum
    from werkzeug.security import generate_password_hash
    
    class AdminBaseView(ModelView):
        def is_accessible(self):
            try:
                return current_user.is_authenticated and current_user.user_type == UserTypeEnum.admin
            except:
                return False
        
        def inaccessible_callback(self, name, **kwargs):
            return redirect(url_for('auth.login', next=request.url))
    
    class UserAdminView(AdminBaseView):
        column_list = ['username', 'user_type', 'is_active']
        form_columns = ['username', 'password', 'user_type', 'is_active']
        
        def on_model_change(self, form, model, is_created):
            if is_created or form.password.data:
                model.password = generate_password_hash(form.password.data)
    
    admin_instance.add_view(UserAdminView(User, db.session))
    admin_instance.add_view(ModelView(Stock, db.session))
    admin_instance.add_view(ModelView(Form, db.session))
    admin_instance.add_view(ModelView(DetailForm, db.session))
    admin_instance.add_view(ModelView(UserUUID, db.session))


def setup_swagger(app):
    """Configure Swagger documentation"""
    import os
    
    swagger_config = {
        "headers": [],
        "specs": [{
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api-docs"
    }
    
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Proyecto Stock API",
            "description": "API para gestión de inventario",
            "version": os.environ.get('APP_VERSION', '0.1.0'),
            "contact": {"name": "API Support"}
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme"
            }
        },
        "security": [{"Bearer": []}]
    }
    
    Swagger(app, config=swagger_config, template=swagger_template)


def init_default_admin():
    """Initialize default admin user if not exists"""
    from .models import User, UserTypeEnum
    from werkzeug.security import generate_password_hash
    
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            password=generate_password_hash('admin123'),
            user_type=UserTypeEnum.admin,
            is_active=True
        )
        db.session.add(admin_user)
        db.session.commit()
