# src/app.py
import os 

from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from api.models import db, User, Stock, Form, DetailForm, UserUUID  # Verifica que estas importaciones sean correctas
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la aplicación Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///C:/Users/SRV/Stock/proyecto-stock/instance/mi_base_datos.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('FLASK_APP_KEY', 'mi_secreto')

# Inicializa la base de datos con la configuración de la app
db.init_app(app)
print(f'DATABASE_URL: {app.config["SQLALCHEMY_DATABASE_URI"]}')
# Inicializa Flask-Migrate
migrate = Migrate(app, db)

# Configuración de Flask-Admin
admin = Admin(app, name='Panel de Administración', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Stock, db.session))
admin.add_view(ModelView(Form, db.session))
admin.add_view(ModelView(DetailForm, db.session))
admin.add_view(ModelView(UserUUID, db.session))

# Crear las tablas en la base de datos si no existen
with app.app_context():
    db.create_all()

# Ruta de prueba
@app.route('/')
def index():
    return "<h1>Bienvenido a la aplicación!</h1>"

if __name__ == '__main__':
    app.run(port=3001, debug=True)
