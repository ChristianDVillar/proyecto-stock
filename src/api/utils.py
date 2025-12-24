"""
Utility functions for error handling and validation
"""
from flask import jsonify
from functools import wraps
import re

def validate_barcode(barcode):
    """Validate barcode format"""
    if not barcode or not isinstance(barcode, str):
        return False, "El código de barras debe ser una cadena de texto"
    if len(barcode.strip()) == 0:
        return False, "El código de barras no puede estar vacío"
    if len(barcode) > 50:
        return False, "El código de barras no puede exceder 50 caracteres"
    return True, None

def validate_inventario(inventario):
    """Validate inventario code"""
    if not inventario or not isinstance(inventario, str):
        return False, "El código de inventario debe ser una cadena de texto"
    if len(inventario.strip()) == 0:
        return False, "El código de inventario no puede estar vacío"
    if len(inventario) > 50:
        return False, "El código de inventario no puede exceder 50 caracteres"
    return True, None

def validate_modelo(modelo):
    """Validate modelo"""
    if not modelo or not isinstance(modelo, str):
        return False, "El modelo debe ser una cadena de texto"
    if len(modelo.strip()) == 0:
        return False, "El modelo no puede estar vacío"
    if len(modelo) > 50:
        return False, "El modelo no puede exceder 50 caracteres"
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

