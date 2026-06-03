from flask import Blueprint, request, jsonify, make_response, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, get_jwt_identity, jwt_required,
    set_access_cookies, set_refresh_cookies, unset_refresh_cookies,
    get_jwt, verify_jwt_in_request
)
from werkzeug.security import generate_password_hash, check_password_hash
from .tenant_utils import assign_user_tenant, ensure_default_tenant
from .models import db, User, UserTypeEnum
from .utils import validate_username, validate_password, validate_request_data, error_handler
import datetime

auth = Blueprint('auth', __name__)

@auth.after_request
def after_request(response):
    """Ensure proper CORS headers are set for all auth routes"""
    origin = request.headers.get('Origin', 'http://localhost:3000')
    response.headers.update({
        'Access-Control-Allow-Origin': origin,
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, Accept, X-Requested-With',
        'Access-Control-Expose-Headers': 'Authorization',
        'Vary': 'Origin'
    })
    return response

@auth.route('/debug', methods=['GET'])
def debug_session():
    """Debug endpoint to check session state. Returns valid_token for AuthStore.verifyToken()."""
    try:
        valid_token = False
        user_identity = None
        try:
            verify_jwt_in_request()
            valid_token = True
            user_identity = get_jwt_identity()
        except Exception as e:
            if current_app.debug:
                current_app.logger.debug("Token verification failed: %s", str(e))

        session_info = {
            'valid_token': valid_token,
            'user_identity': user_identity,
            'jwt_config': {
                'token_location': current_app.config.get('JWT_TOKEN_LOCATION', 'headers'),
                'header_name': current_app.config.get('JWT_HEADER_NAME', 'Authorization'),
                'header_type': current_app.config.get('JWT_HEADER_TYPE', 'Bearer'),
                'cookie_name': current_app.config.get('JWT_ACCESS_COOKIE_NAME', 'access_token_cookie')
            }
        }
        return jsonify(session_info)
    except Exception as e:
        current_app.logger.exception('auth/debug error')
        return jsonify({'error': str(e), 'valid_token': False}), 500

@auth.route('/register', methods=['POST'])
@error_handler
def register():
    from .services.auth_service import AuthService
    data = request.get_json()
    required_fields = ['username', 'password']
    is_valid, error_msg = validate_request_data(required_fields, data)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    username_valid, username_error = validate_username(data['username'])
    if not username_valid:
        return jsonify({'error': username_error}), 400
    password_valid, password_error = validate_password(data['password'])
    if not password_valid:
        return jsonify({'error': password_error}), 400
    new_user, err = AuthService.register_user(data['username'], data['password'])
    if err:
        return jsonify({'error': err}), 400
    return jsonify({
        'message': 'Usuario registrado exitosamente',
        'user': {'id': new_user.id, 'username': new_user.username, 'user_type': new_user.user_type.value}
    }), 201

def _log_failed_login(username, reason, ip):
    """Registra intento de login fallido (para auditoría y rate limit por usuario)."""
    try:
        current_app.logger.warning(
            'login_failed',
            extra={
                'username': username,
                'reason': reason,
                'ip': ip,
                'path': request.path,
            }
        )
    except Exception:
        pass


@auth.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        ip = request.remote_addr or 'unknown'
        username = (data or {}).get('username', '')

        if not data or 'username' not in data or 'password' not in data:
            _log_failed_login(username, 'missing_credentials', ip)
            return jsonify({'error': 'Se requiere usuario y contraseña'}), 400

        user = User.query.filter_by(username=data['username']).first()

        if not user or not check_password_hash(user.password, data['password']):
            _log_failed_login(username, 'invalid_credentials', ip)
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401

        if not user.is_active:
            _log_failed_login(username, 'user_inactive', ip)
            return jsonify({'error': 'Usuario inactivo'}), 401

        if not user.tenant_id:
            assign_user_tenant(user)
            db.session.commit()

        additional_claims = {
            'username': user.username,
            'user_type': user.user_type.value,
            'tenant_id': user.tenant_id,
            'created_at': datetime.datetime.utcnow().isoformat()
        }
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims=additional_claims
        )
        refresh_token = create_refresh_token(identity=str(user.id))

        user_type = user.user_type.value if isinstance(user.user_type, UserTypeEnum) else user.user_type
        response_data = {
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'user_type': user_type,
                'tenant_id': user.tenant_id,
            }
        }

        response = make_response(jsonify(response_data))
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        response.headers['Authorization'] = f'Bearer {access_token}'
        return response

    except Exception as e:
        current_app.logger.exception('login_error')
        return jsonify({'error': 'Error en el servidor'}), 500

@auth.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Emite un nuevo access token usando el refresh token (cookie HTTP-only)."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user or not user.is_active:
            return jsonify({'error': 'Usuario no encontrado o inactivo'}), 401
        additional_claims = {
            'username': user.username,
            'user_type': user.user_type.value,
            'tenant_id': user.tenant_id,
            'created_at': datetime.datetime.utcnow().isoformat()
        }
        access_token = create_access_token(
            identity=str(user_id),
            additional_claims=additional_claims
        )
        response = make_response(jsonify({'access_token': access_token}))
        set_access_cookies(response, access_token)
        response.headers['Authorization'] = f'Bearer {access_token}'
        return response
    except Exception as e:
        current_app.logger.exception('refresh_error')
        return jsonify({'error': 'Error al renovar token'}), 500


@auth.route('/logout', methods=['POST'])
@jwt_required(optional=True)
def logout():
    """Limpia cookies de refresh (el cliente debe borrar el access token)."""
    response = jsonify({'message': 'Sesión cerrada'})
    unset_refresh_cookies(response)
    return response


@auth.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        jwt_data = get_jwt()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        response_data = {
            'username': user.username,
            'user_type': user.user_type.value,
            'tenant_id': user.tenant_id,
            'is_active': user.is_active,
            'token_info': {
                'exp': jwt_data.get('exp'),
                'created_at': jwt_data.get('created_at')
            }
        }
        response = jsonify(response_data)

        # Renovar access token si expira en menos de 5 min (el cliente puede usar /refresh si no)
        if jwt_data.get('exp'):
            exp_timestamp = jwt_data['exp']
            current_timestamp = datetime.datetime.utcnow().timestamp()
            if exp_timestamp - current_timestamp < 300:
                new_token = create_access_token(
                    identity=str(user.id),
                    additional_claims={
                        'username': user.username,
                        'user_type': user.user_type.value,
                        'created_at': datetime.datetime.utcnow().isoformat()
                    }
                )
                response.headers['Authorization'] = f'Bearer {new_token}'
                set_access_cookies(response, new_token)

        return response, 200
    except Exception as e:
        current_app.logger.exception('me_error')
        return jsonify({'error': str(e)}), 500 