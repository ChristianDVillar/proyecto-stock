"""Add missing columns to stock table (e.g. deleted_at).

Revision ID: 002_add_stock
Revises: 001_initial
Create Date: 2025-02-27

If the stock table was created with an older schema, this adds columns
that the current model expects (no such column: stock.d...).
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))

from alembic import op
import sqlalchemy as sa

revision = '002_add_stock'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def _column_exists(connection, table, column):
    """Return True if column exists in table."""
    dialect = connection.dialect.name
    if dialect == 'sqlite':
        # SQLite: pragma_table_info('table_name')
        r = connection.execute(sa.text(
            f"SELECT 1 FROM pragma_table_info('{table}') WHERE name=:name"
        ), {"name": column})
        return r.scalar() is not None
    if dialect == 'postgresql':
        r = connection.execute(sa.text(
            "SELECT 1 FROM information_schema.columns WHERE table_name=:table AND column_name=:name"
        ), {"table": table, "name": column})
        return r.scalar() is not None
    return False


def upgrade():
    connection = op.get_bind()
    # Add deleted_at for soft delete (fixes: no such column stock.deleted_at)
    if not _column_exists(connection, 'stock', 'deleted_at'):
        if connection.dialect.name == 'sqlite':
            op.execute("ALTER TABLE stock ADD COLUMN deleted_at DATETIME")
        else:
            op.add_column('stock', sa.Column('deleted_at', sa.DateTime(), nullable=True))


def downgrade():
    # SQLite doesn't support DROP COLUMN before 3.35; skip to avoid breaking
    if op.get_bind().dialect.name != 'sqlite':
        op.drop_column('stock', 'deleted_at')
