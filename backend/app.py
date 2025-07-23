# src/app.py
import os 
import logging
from flask import Flask, jsonify, g, redirect, url_for, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from models import db, User, Stock, Form, DetailForm, UserUUID, UserTypeEnum
from dotenv import load_dotenv
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
from werkzeug.security import generate_password_hash
from sqlalchemy import event
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_login import LoginManager, current_user, UserMixin

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Asegurarse de que el directorio instance existe
instance_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

# Configuración de la aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Configuración de CORS
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:3004", "http://localhost:3005"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept", "X-Requested-With"],
        "expose_headers": ["Authorization"],
        "supports_credentials": True
    }
})

# Configuración de JWT
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'tu-clave-secreta-aqui')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['JWT_ERROR_MESSAGE_KEY'] = 'error'
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token_cookie'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_COOKIE_SECURE'] = False
app.config['JWT_SESSION_COOKIE'] = False
app.config['JWT_COOKIE_SAMESITE'] = 'Lax'

jwt = JWTManager(app)

@jwt.user_identity_loader
def user_identity_lookup(user):
    print(f"Identity lookup for user: {user}, type: {type(user)}")  # Debug log
    if isinstance(user, dict):
        return str(user.get('id'))
    return str(user) if user is not None else None

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    print(f"User lookup with data: {jwt_data}")  # Debug log
    try:
        identity = jwt_data["sub"]
        print(f"Looking up user with ID: {identity}, type: {type(identity)}")  # Debug log
        # Convertir el ID de string a entero para la búsqueda
        user_id = int(identity)
        user = User.query.filter_by(id=user_id).one_or_none()
        print(f"Found user: {user}")  # Debug log
        return user
    except (ValueError, KeyError) as e:
        print(f"Error in user lookup: {str(e)}")  # Debug log
        return None

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    print(f"Checking token: {jwt_payload}")  # Debug log
    try:
        # Verificar que el subject sea una cadena válida
        if not isinstance(jwt_payload.get('sub'), str):
            print(f"Invalid subject type: {type(jwt_payload.get('sub'))}")
            return True
        return False
    except Exception as e:
        print(f"Error checking token: {str(e)}")
        return True

# Manejador de errores JWT
@jwt.invalid_token_loader
def invalid_token_callback(error_string):
    print(f"Invalid token error: {error_string}")  # Debug log
    return jsonify({
        'error': 'Token inválido',
        'message': f'El token no es válido: {error_string}'
    }), 401

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    print(f"Expired token: {jwt_payload}")  # Debug log
    return jsonify({
        'error': 'Token expirado',
        'message': 'El token ha expirado. Por favor, inicie sesión nuevamente.'
    }), 401

@jwt.unauthorized_loader
def unauthorized_callback(error_string):
    print(f"Unauthorized error: {error_string}")  # Debug log
    return jsonify({
        'error': 'Token no proporcionado',
        'message': f'No se proporcionó un token válido: {error_string}'
    }), 401

# Configuración de la base de datos
db_path = os.path.join(instance_path, 'mi_base_datos.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_size': 5,
    'max_overflow': 10
}

# Inicializa la base de datos con la configuración de la app
db.init_app(app)

# Configuración de Flask-Admin
admin = Admin(app, name='Panel de Administración', template_mode='bootstrap3')

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_type == UserTypeEnum.admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

# Agregar vistas de administración
admin.add_view(AdminModelView(User, db.session))
admin.add_view(AdminModelView(Stock, db.session))
admin.add_view(AdminModelView(Form, db.session))
admin.add_view(AdminModelView(DetailForm, db.session))

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.after_request
def after_request(response):
    """Add CORS headers to all responses"""
    origin = request.headers.get('Origin', 'http://localhost:3004')
    allowed_origins = ['http://localhost:3000', 'http://localhost:3004']
    
    if origin in allowed_origins:
        response.headers.update({
            'Access-Control-Allow-Origin': origin,
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, Accept, X-Requested-With',
            'Access-Control-Expose-Headers': 'Authorization',
            'Vary': 'Origin'
        })
    return response

# Importar y registrar blueprints
from auth import auth as auth_blueprint
from users import users as users_blueprint
from routes import api as api_blueprint
from forms import forms as forms_blueprint

app.register_blueprint(auth_blueprint, url_prefix='/api/auth')
app.register_blueprint(users_blueprint, url_prefix='/api/users')
app.register_blueprint(api_blueprint, url_prefix='/api')
app.register_blueprint(forms_blueprint, url_prefix='/api/forms')

# Crear las tablas de la base de datos
with app.app_context():
    db.create_all()
    print("Base de datos inicializada y tablas creadas.")

    # Crear usuario admin si no existe
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            password=generate_password_hash('admin'),
            user_type=UserTypeEnum.admin,
            is_active=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Usuario admin creado")

print("Tablas creadas correctamente")

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
