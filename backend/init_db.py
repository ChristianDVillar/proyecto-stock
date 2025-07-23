import os
from app import app, db
from models import User, UserTypeEnum
from werkzeug.security import generate_password_hash

def init_database():
    with app.app_context():
        # Asegurarse de que el directorio instance existe
        if not os.path.exists('instance'):
            os.makedirs('instance')
            print("Directorio instance creado.")

        # Crear todas las tablas
        db.create_all()
        print("Tablas creadas exitosamente.")

        # Verificar si ya existe un usuario administrador
        admin_exists = User.query.filter_by(user_type=UserTypeEnum.admin).first()
        
        if not admin_exists:
            # Crear usuario administrador por defecto
            admin_user = User(
                username='admin',
                password=generate_password_hash('admin123'),  # Contraseña por defecto
                user_type=UserTypeEnum.admin,
                is_active=True
            )
            
            try:
                db.session.add(admin_user)
                db.session.commit()
                print("\n¡Usuario administrador creado exitosamente!")
                print("----------------------------------------")
                print("Username: admin")
                print("Password: admin123")
                print("----------------------------------------")
                print("¡Por favor, cambia esta contraseña después de iniciar sesión!")
            except Exception as e:
                db.session.rollback()
                print(f"Error al crear usuario administrador: {str(e)}")
        else:
            print("Ya existe al menos un usuario administrador en la base de datos.")

        # Mostrar información de las tablas
        print("\nTablas en la base de datos:")
        for table in db.metadata.tables.keys():
            print(f"- {table}")

if __name__ == '__main__':
    print("Iniciando configuración de la base de datos...")
    init_database()
    print("\nProceso completado.") 