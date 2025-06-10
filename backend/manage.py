# src/api/manage.py
from flask_migrate import Migrate, upgrade
from api.models import db
from app import app  # Importa desde la ruta relativa src.app

# Inicializa Flask-Migrate
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(port=3001, debug=True)
