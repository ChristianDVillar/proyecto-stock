from flask import Blueprint, request, jsonify, make_response, current_app
from flask_jwt_extended import (
    create_access_token, get_jwt_identity, jwt_required, set_access_cookies,
    get_jwt, verify_jwt_in_request
)
from werkzeug.security import generate_password_hash, check_password_hash
from .models import db, User, UserTypeEnum
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
    """Debug endpoint to check session state"""
    try:
        # Intentar verificar el token sin requerir autenticación
        valid_token = False
        user_identity = None
        try:
            verify_jwt_in_request()
            valid_token = True
            user_identity = get_jwt_identity()
        except Exception as e:
            print(f"Token verification failed: {str(e)}")

        # Recopilar información de la sesión
        session_info = {
            'request_headers': dict(request.headers),
            'cookies': dict(request.cookies),
            'valid_token': valid_token,
            'user_identity': user_identity,
            'jwt_config': {
                'token_location': current_app.config['JWT_TOKEN_LOCATION'],
                'header_name': current_app.config['JWT_HEADER_NAME'],
                'header_type': current_app.config['JWT_HEADER_TYPE'],
                'cookie_name': current_app.config['JWT_ACCESS_COOKIE_NAME']
            }
        }
        
        return jsonify(session_info)
    except Exception as e:
        print(f"Debug endpoint error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        print(f"Register attempt with data: {data}")  # Debug log
        
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400
            
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Se requieren nombre de usuario y contraseña'}), 400

        existing_user = User.query.filter_by(username=data['username']).first()
        if existing_user:
            return jsonify({'error': 'El nombre de usuario ya existe'}), 400

        # Crear nuevo usuario como usuario regular
        new_user = User(
            username=data['username'],
            password=generate_password_hash(data['password']),
            user_type=UserTypeEnum.user,
            is_active=True
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            print(f"Usuario creado exitosamente: {new_user.username}")  # Debug log
            return jsonify({
                'message': 'Usuario registrado exitosamente',
                'user': {
                    'id': new_user.id,
                    'username': new_user.username,
                    'user_type': new_user.user_type.value
                }
            }), 201
        except Exception as e:
            db.session.rollback()
            print(f"Error al guardar usuario en la base de datos: {str(e)}")  # Debug log
            return jsonify({'error': 'Error al crear el usuario en la base de datos'}), 500

    except Exception as e:
        print(f"Error en registro: {str(e)}")  # Debug log
        return jsonify({'error': str(e)}), 500

@auth.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        print(f"Login attempt for user: {data.get('username')}")  # Debug log
        
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Se requiere usuario y contraseña'}), 400
        
        user = User.query.filter_by(username=data['username']).first()
        print(f"Found user: {user}, user_type: {getattr(user, 'user_type', None)}")  # Debug log
        
        if not user or not check_password_hash(user.password, data['password']):
            return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Usuario inactivo'}), 401

        # Crear el token con el ID del usuario como string y datos adicionales
        additional_claims = {
            'username': user.username,
            'user_type': user.user_type.value,
            'created_at': datetime.datetime.utcnow().isoformat()
        }
        
        print(f"Creating token for user ID: {user.id} with claims: {additional_claims}")  # Debug log
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims=additional_claims
        )
        print(f"Token created successfully: {access_token}")  # Debug log
        
        # Asegurarse de que el tipo de usuario sea el valor del enum
        user_type = user.user_type.value if isinstance(user.user_type, UserTypeEnum) else user.user_type
        print(f"User type for response: {user_type}")  # Debug log
        
        response_data = {
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'user_type': user_type
            }
        }
        print(f"Response data prepared: {response_data}")  # Debug log
        
        # Crear la respuesta
        response = make_response(jsonify(response_data))
        
        # Set the JWT token in cookies
        set_access_cookies(response, access_token)
        
        # Set Authorization header
        response.headers['Authorization'] = f'Bearer {access_token}'
        
        print(f"Response headers set: {dict(response.headers)}")  # Debug log
        return response
        
    except Exception as e:
        print(f"Error en login: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")  # Debug log
        return jsonify({'error': 'Error en el servidor'}), 500

@auth.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        # Obtener el token actual y sus claims
        jwt_data = get_jwt()
        user_id = get_jwt_identity()
        
        print(f"Token data in /me: {jwt_data}")  # Debug log
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        response_data = {
            'username': user.username,
            'user_type': user.user_type.value,
            'is_active': user.is_active,
            'token_info': {
                'exp': jwt_data.get('exp'),
                'created_at': jwt_data.get('created_at')
            }
        }
        
        response = jsonify(response_data)
        
        # Renovar el token si está próximo a expirar
        if jwt_data.get('exp'):
            exp_timestamp = jwt_data['exp']
            current_timestamp = datetime.datetime.utcnow().timestamp()
            # Si el token expira en menos de 30 minutos, renovarlo
            if exp_timestamp - current_timestamp < 1800:
                new_token = create_access_token(identity=str(user.id))
                response.headers['Authorization'] = f'Bearer {new_token}'
                set_access_cookies(response, new_token)
        
        return response, 200

    except Exception as e:
        print(f"Error in /me: {str(e)}")
        return jsonify({'error': str(e)}), 500 