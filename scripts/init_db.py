#!/usr/bin/env python
"""
Script de inicialización de base de datos
Ejecuta migraciones y crea usuario admin por defecto
"""
import os
import sys

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import create_app
from app.models import db, User, UserTypeEnum
from werkzeug.security import generate_password_hash

def init_database():
    """Inicializa la base de datos"""
    # Obtener entorno
    env = os.environ.get('FLASK_ENV', 'production')
    
    # Crear aplicación
    app = create_app(env)
    
    with app.app_context():
        try:
            # Crear todas las tablas
            print("Creating database tables...")
            db.create_all()
            print("✓ Tables created successfully")
            
            # Crear usuario admin si no existe
            admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            
            admin_user = User.query.filter_by(username=admin_username).first()
            if not admin_user:
                print("Creating default admin user...")
                admin_user = User(
                    username=admin_username,
                    password=generate_password_hash(admin_password),
                    user_type=UserTypeEnum.admin,
                    is_active=True
                )
                db.session.add(admin_user)
                db.session.commit()
                print("✓ Admin user created successfully")
                print(f"  Username: {admin_username}")
                if env == 'development':
                    print(f"  Password: {admin_password} (⚠️ Change in production!)")
                else:
                    print("  Password: [HIDDEN] (set via ADMIN_PASSWORD env var)")
            else:
                print("✓ Admin user already exists")
            
            print("\nDatabase initialization completed successfully!")
            return 0
            
        except Exception as e:
            print(f"✗ Error initializing database: {str(e)}")
            db.session.rollback()
            return 1

if __name__ == '__main__':
    sys.exit(init_database())

