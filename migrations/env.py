# Alembic env.py for Flask-Migrate
# Run from project root with: PYTHONPATH=src FLASK_APP=src/run.py flask db <command>
import os
import sys
from pathlib import Path

# Añadir src al path para importar la app
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'src'))

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

config = context.config
config_file = config.config_file_name
if config_file is not None:
    p = Path(config_file)
    if not p.is_file():
        root_ini = Path(__file__).resolve().parent.parent / 'alembic.ini'
        if root_ini.is_file():
            config_file = str(root_ini)
    if Path(config_file).is_file():
        fileConfig(config_file)

# Importar app y db (sin Flask-Admin: run.py ya puede haberlo cargado)
os.environ.setdefault('FLASK_SKIP_ADMIN', '1')

from app import create_app
from app.models import db

app = create_app(os.environ.get('FLASK_ENV', 'development'))
target_metadata = db.metadata

def get_url():
    return app.config['SQLALCHEMY_DATABASE_URI']

def run_migrations_offline():
    context.configure(url=get_url(), target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    with app.app_context():
        connectable = engine_from_config(
            {'sqlalchemy.url': get_url()},
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
        with connectable.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)
            with context.begin_transaction():
                context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
