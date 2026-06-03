"""
Flask extensions initialization
Centralized extension instances
"""
from flask_jwt_extended import JWTManager, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_admin import Admin


def get_rate_limit_key():
    """Clave para rate limit: por user_id si hay JWT, si no por IP."""
    try:
        uid = get_jwt_identity()
        if uid:
            return f"user:{uid}"
    except Exception:
        pass
    return get_remote_address()


# Initialize extensions (will be configured in app factory)
jwt = JWTManager()
limiter = Limiter(
    key_func=get_rate_limit_key,
    default_limits=["200 per day", "50 per hour"]
)
login_manager = LoginManager()
admin = Admin(name='Panel de Administración', url='/admin')

