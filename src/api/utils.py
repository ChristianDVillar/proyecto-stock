"""
Utility functions for error handling, validation and authorization helpers.
"""
from flask import jsonify
from functools import wraps
import re
from flask_jwt_extended import get_jwt_identity
from .models import User, UserTypeEnum


def _validate_string(value, field_name_es, max_len=50):
    """Valida un string no vacío con longitud máxima. Devuelve (ok: bool, error: str|None)."""
    if not value or not isinstance(value, str):
        return False, f"{field_name_es} debe ser una cadena de texto"
    if len(value.strip()) == 0:
        return False, f"{field_name_es} no puede estar vacío"
    if len(value) > max_len:
        return False, f"{field_name_es} no puede exceder {max_len} caracteres"
    return True, None


def validate_barcode(barcode):
    """Validate barcode format"""
    return _validate_string(barcode, "El código de barras", 50)


def validate_inventario(inventario):
    """Validate inventario code"""
    return _validate_string(inventario, "El código de inventario", 50)


def validate_modelo(modelo):
    """Validate modelo"""
    return _validate_string(modelo, "El modelo", 50)


def validate_descripcion(descripcion):
    """Validate descripcion (optional, max 200 chars)."""
    if descripcion is None or descripcion == '':
        return True, None
    if not isinstance(descripcion, str):
        return False, "La descripción debe ser texto"
    if len(descripcion) > 200:
        return False, "La descripción no puede exceder 200 caracteres"
    return True, None


def validate_cantidad(cantidad):
    """Validate cantidad"""
    try:
        cantidad_int = int(cantidad)
        if cantidad_int <= 0:
            return False, "La cantidad debe ser mayor que 0"
        if cantidad_int > 1000000:
            return False, "La cantidad no puede exceder 1,000,000"
        return True, None
    except (ValueError, TypeError):
        return False, "La cantidad debe ser un número válido"

def validate_username(username):
    """Validate username"""
    if not username or not isinstance(username, str):
        return False, "El nombre de usuario debe ser una cadena de texto"
    if len(username.strip()) < 3:
        return False, "El nombre de usuario debe tener al menos 3 caracteres"
    if len(username) > 80:
        return False, "El nombre de usuario no puede exceder 80 caracteres"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "El nombre de usuario solo puede contener letras, números y guiones bajos"
    return True, None

def validate_password(password):
    """Validate password"""
    if not password or not isinstance(password, str):
        return False, "La contraseña debe ser una cadena de texto"
    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres"
    if len(password) > 120:
        return False, "La contraseña no puede exceder 120 caracteres"
    return True, None

def handle_api_error(error, status_code=500):
    """Standard error response handler"""
    error_response = {
        'error': str(error),
        'status_code': status_code
    }
    return jsonify(error_response), status_code

def validate_request_data(required_fields, data):
    """Validate that required fields are present in request data"""
    if not data:
        return False, "No se recibieron datos en la petición"
    
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return False, f"Faltan los siguientes campos requeridos: {', '.join(missing_fields)}"
    
    return True, None

def error_handler(f):
    """Decorator for error handling"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return handle_api_error(str(e), 400)
        except KeyError as e:
            return handle_api_error(f"Campo faltante: {str(e)}", 400)
        except Exception as e:
            import traceback
            print(f"Error in {f.__name__}: {str(e)}")
            print(traceback.format_exc())
            return handle_api_error("Error interno del servidor", 500)
    return decorated_function


def role_required(*roles):
    """
    Simple RBAC decorator based on User.user_type.
    Usage:
        @jwt_required()
        @role_required('admin')
        def some_view(): ...
    """
    # Normalizamos a valores del Enum (e.g. 'admin', 'user')
    allowed = {r.value if isinstance(r, UserTypeEnum) else str(r) for r in roles}

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                user_id = get_jwt_identity()
                if not user_id:
                    return jsonify({'error': 'No autenticado'}), 401
                user = User.query.get(int(user_id))
                if not user:
                    return jsonify({'error': 'Usuario no encontrado'}), 404
                user_type = user.user_type.value if isinstance(user.user_type, UserTypeEnum) else str(user.user_type)
                if user_type not in allowed:
                    return jsonify({'error': 'No autorizado'}), 403
            except Exception:
                return jsonify({'error': 'No autorizado'}), 403
            return fn(*args, **kwargs)

        return wrapper

    return decorator

