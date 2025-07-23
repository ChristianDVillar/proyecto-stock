from app import app, db
from models import User, UserTypeEnum
from werkzeug.security import generate_password_hash

def create_admin_user(username, password):
    with app.app_context():
        # Verificar si el usuario ya existe
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"El usuario {username} ya existe.")
            return

        # Crear nuevo usuario administrador
        admin_user = User(
            username=username,
            password=generate_password_hash(password),
            user_type=UserTypeEnum.admin,
            is_active=True
        )

        try:
            db.session.add(admin_user)
            db.session.commit()
            print(f"Usuario administrador '{username}' creado exitosamente.")
        except Exception as e:
            db.session.rollback()
            print(f"Error al crear el usuario: {str(e)}")

if __name__ == '__main__':
    username = input("Ingrese el nombre de usuario para el administrador: ")
    password = input("Ingrese la contraseña para el administrador: ")
    create_admin_user(username, password) 