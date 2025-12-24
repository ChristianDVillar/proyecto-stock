# src/app.py
import os 

from flask import Flask, jsonify, g, redirect, url_for, request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from api.models import db, User, Stock, Form, DetailForm, UserUUID, UserTypeEnum
from dotenv import load_dotenv
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
from api.routes import api
from api.auth import auth
from api.users import users
from werkzeug.security import generate_password_hash
from sqlalchemy import event
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_login import LoginManager, current_user, UserMixin
from flasgger import Swagger

# Cargar variables de entorno
load_dotenv()

# Asegurarse de que el directorio instance existe
instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

# Configuración de la aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Configuración de CORS desde variables de entorno
cors_origins = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5000').split(',')
CORS(app, 
     resources={
        r"/*": {
            "origins": cors_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Accept", "X-Requested-With"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "send_wildcard": False,
            "max_age": 3600
        }
     },
     supports_credentials=True
)

# Configuración de JWT desde variables de entorno
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', os.environ.get('SECRET_KEY', 'your-secret-key-here'))
jwt_expires_days = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES_DAYS', '1'))
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=jwt_expires_days)
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
app.config['JWT_ERROR_MESSAGE_KEY'] = 'error'
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token_cookie'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['JWT_COOKIE_SECURE'] = os.environ.get('JWT_COOKIE_SECURE', 'False').lower() == 'true'
app.config['JWT_SESSION_COOKIE'] = False
app.config['JWT_COOKIE_SAMESITE'] = os.environ.get('JWT_COOKIE_SAMESITE', 'Lax')

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

# Configuración de la base de datos desde variables de entorno
database_uri = os.environ.get('DATABASE_URI')
if not database_uri:
    db_path = os.path.join(instance_path, 'mi_base_datos.db')
    database_uri = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_size': 5,
    'max_overflow': 10
}

# Inicializa la base de datos con la configuración de la app
db.init_app(app)

# Configurar el manejo de sesiones
@app.before_request
def before_request():
    if not hasattr(g, 'session'):
        g.session = db.session()

@app.teardown_appcontext
def teardown_request(exception=None):
    if hasattr(g, 'session'):
        g.session.close()
        delattr(g, 'session')

# Configurar Swagger para documentación de API
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
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
        "contact": {
            "name": "API Support"
        }
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
        }
    },
    "security": [
        {
            "Bearer": []
        }
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Registrar los blueprints
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(auth, url_prefix='/api/auth')
app.register_blueprint(users, url_prefix='/api/users')

# Crear todas las tablas si no existen
with app.app_context():
    db.create_all()
    print("Tablas creadas correctamente")

# Inicializa Flask-Migrate
migrate = Migrate(app, db)

def init_db():
    with app.app_context():
        try:
            # Crear todas las tablas si no existen
            db.create_all()
            print("Tablas creadas correctamente")
            
            # Crear usuario administrador por defecto si no existe
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
                print('Usuario administrador creado con éxito')
                print('Usuario: admin')
                print('Contraseña: admin123')
        except Exception as e:
            db.session.rollback()
            print(f'Error en la inicialización de la base de datos: {str(e)}')

# Configuración de Flask-Admin
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

# Configuración de Flask-Admin
admin = Admin(app, name='Panel de Administración', template_mode='bootstrap3', url='/admin')
admin.add_view(UserAdminView(User, db.session))
admin.add_view(ModelView(Stock, db.session))
admin.add_view(ModelView(Form, db.session))
admin.add_view(ModelView(DetailForm, db.session))
admin.add_view(ModelView(UserUUID, db.session))

# Manejadores de error para devolver JSON en lugar de HTML
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Recurso no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    if hasattr(g, 'session'):
        g.session.rollback()
    return jsonify({'error': 'Error interno del servidor'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    if hasattr(g, 'session'):
        g.session.rollback()
    # Manejar errores no HTTP
    return jsonify({
        'error': str(e),
        'type': str(type(e).__name__)
    }), 500

# Ruta de prueba
@app.route('/')
def index():
    return jsonify({'message': 'API funcionando correctamente'})

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

if __name__ == '__main__':
    init_db()
    app.run(port=5000, debug=True)
else:
    init_db()
