"""
Flask extensions initialization
Centralized extension instances
"""
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_admin import Admin

# Initialize extensions (will be configured in app factory)
jwt = JWTManager()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
login_manager = LoginManager()
admin = Admin(name='Panel de Administración', template_mode='bootstrap3', url='/admin')

