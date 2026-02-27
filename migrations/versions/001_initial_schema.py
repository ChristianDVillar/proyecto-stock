"""Initial schema from models.

Revision ID: 001_initial
Revises:
Create Date: 2025-01-01 00:00:00

"""
import os
import sys
from pathlib import Path

# Asegurar que podemos importar la app desde src
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))

from alembic import op
import sqlalchemy as sa
from app import create_app
from app.models import db

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    with app.app_context():
        db.metadata.create_all(op.get_bind())


def downgrade():
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    with app.app_context():
        db.metadata.drop_all(op.get_bind())
