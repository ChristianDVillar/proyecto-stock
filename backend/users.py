from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from models import db, User, UserTypeEnum

users = Blueprint('users', __name__)

@users.route('', methods=['GET'])
@jwt_required()
def get_users():
    try:
        # Get the current user ID
        current_user_id = get_jwt_identity()
        print(f"Current user ID: {current_user_id}")  # Debug log
        
        if not current_user_id:
            return jsonify({'error': 'Token inválido o expirado'}), 401
        
        # Verificar si el usuario actual es admin
        current_user = User.query.get(current_user_id)
        print(f"Current user: {current_user}, type: {getattr(current_user, 'user_type', None)}")  # Debug log
        
        if not current_user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
            
        if not current_user.user_type == UserTypeEnum.admin:
            print(f"User type mismatch: {current_user.user_type} != {UserTypeEnum.admin}")  # Debug log
            return jsonify({'error': 'No autorizado'}), 403

        users = User.query.all()
        users_data = [user.to_dict() for user in users]
        print(f"Returning {len(users_data)} users")  # Debug log
        return jsonify({
            'users': users_data
        }), 200
    except Exception as e:
        import traceback
        print(f"Error in get_users: {str(e)}")  # Debug log
        print(f"Traceback: {traceback.format_exc()}")  # Debug log
        return jsonify({'error': str(e)}), 500

@users.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    try:
        # Verificar si el usuario actual es admin
        current_user = User.query.get(get_jwt_identity())
        if not current_user or current_user.user_type != UserTypeEnum.admin:
            return jsonify({'error': 'No autorizado'}), 403

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users.route('', methods=['POST'])
@jwt_required()
def create_user():
    try:
        # Verificar si el usuario actual es admin
        current_user = User.query.get(get_jwt_identity())
        if not current_user or current_user.user_type != UserTypeEnum.admin:
            return jsonify({'error': 'No autorizado'}), 403

        data = request.json
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Se requieren nombre de usuario y contraseña'}), 400

        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'El nombre de usuario ya existe'}), 400

        new_user = User(
            username=data['username'],
            password=generate_password_hash(data['password']),
            user_type=UserTypeEnum[data.get('user_type', 'usuario')],
            is_active=data.get('is_active', True)
        )

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            'message': 'Usuario creado exitosamente',
            'user': new_user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    try:
        # Verificar si el usuario actual es admin
        current_user = User.query.get(get_jwt_identity())
        if not current_user or current_user.user_type != UserTypeEnum.admin:
            return jsonify({'error': 'No autorizado'}), 403

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        data = request.json

        # Actualizar campos básicos
        if 'username' in data and data['username'] != user.username:
            if User.query.filter_by(username=data['username']).first():
                return jsonify({'error': 'El nombre de usuario ya existe'}), 400
            user.username = data['username']

        if 'password' in data and data['password']:
            user.password = generate_password_hash(data['password'])

        if 'user_type' in data:
            user.user_type = UserTypeEnum[data['user_type']]

        if 'is_active' in data:
            user.is_active = data['is_active']

        db.session.commit()
        return jsonify({
            'message': 'Usuario actualizado exitosamente',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    try:
        # Verificar si el usuario actual es admin
        current_user = User.query.get(get_jwt_identity())
        if not current_user or current_user.user_type != UserTypeEnum.admin:
            return jsonify({'error': 'No autorizado'}), 403

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        # No permitir eliminar al propio usuario
        if user.id == current_user.id:
            return jsonify({'error': 'No puede eliminar su propio usuario'}), 400

        db.session.delete(user)
        db.session.commit()

        return jsonify({'message': 'Usuario eliminado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 