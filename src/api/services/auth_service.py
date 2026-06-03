"""Servicio de autenticación: registro y validación de usuarios."""
from werkzeug.security import generate_password_hash, check_password_hash

from ..models import db, User, UserTypeEnum


class AuthService:
    @staticmethod
    def register_user(username: str, password: str):
        """Crea un usuario regular. Devuelve (user, error_msg). Si error_msg no es None, no se hizo commit."""
        existing = User.query.filter_by(username=username).first()
        if existing:
            return None, 'El nombre de usuario ya existe'
        user = User(
            username=username,
            password=generate_password_hash(password),
            user_type=UserTypeEnum.user,
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
        return user, None

    @staticmethod
    def get_user_by_username(username: str):
        return User.query.filter_by(username=username).first()

    @staticmethod
    def check_password(user, password: str) -> bool:
        return user and check_password_hash(user.password, password)
