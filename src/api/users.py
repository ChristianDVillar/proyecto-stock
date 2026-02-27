from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from .models import db, User, UserTypeEnum
from .utils import role_required

users = Blueprint('users', __name__)


def _require_admin():
    """
    Obtiene el usuario actual y verifica que sea admin.
    Devuelve (current_user, None) si ok, o (None, (response, status_code)) si hay error.
    """
    user_id = get_jwt_identity()
    if not user_id:
        return None, (jsonify({'error': 'Token inválido o expirado'}), 401)
    try:
        current_user = User.query.get(int(user_id))
    except (TypeError, ValueError):
        return None, (jsonify({'error': 'Usuario no encontrado'}), 404)
    if not current_user:
        return None, (jsonify({'error': 'Usuario no encontrado'}), 404)
    if current_user.user_type != UserTypeEnum.admin:
        return None, (jsonify({'error': 'No autorizado'}), 403)
    return current_user, None


@users.route('', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_users():
    try:
        all_users = User.query.all()
        return jsonify({'users': [u.to_dict() for u in all_users]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users.route('/<int:user_id>', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404

        return jsonify(user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users.route('', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_user():
    try:
        data = request.json
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Se requieren nombre de usuario y contraseña'}), 400

        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'El nombre de usuario ya existe'}), 400

        # Mapear 'usuario' a 'user' para compatibilidad con el frontend
        user_type_str = data.get('user_type', 'usuario')
        if user_type_str == 'usuario':
            user_type_str = 'user'
        
        try:
            user_type_enum = UserTypeEnum[user_type_str]
        except KeyError:
            return jsonify({'error': f'Tipo de usuario inválido: {user_type_str}'}), 400
        
        new_user = User(
            username=data['username'],
            password=generate_password_hash(data['password']),
            user_type=user_type_enum,
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
@role_required('admin')
def update_user(user_id):
    try:
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
            # Mapear 'usuario' a 'user' para compatibilidad con el frontend
            user_type_str = data['user_type']
            if user_type_str == 'usuario':
                user_type_str = 'user'
            try:
                user.user_type = UserTypeEnum[user_type_str]
            except KeyError:
                return jsonify({'error': f'Tipo de usuario inválido: {user_type_str}'}), 400

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
@role_required('admin')
def delete_user(user_id):
    try:
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