"""Fase 2: multi-tenant, multi-almacén, firma digital.

Revision ID: 004_saas_warehouse
Revises: 003_commercial
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))

from alembic import op
import sqlalchemy as sa

revision = '004_saas_warehouse'
down_revision = '003_commercial'
branch_labels = None
depends_on = None


def _table_exists(connection, table):
    if connection.dialect.name == 'sqlite':
        r = connection.execute(sa.text(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=:name"
        ), {"name": table})
        return r.scalar() is not None
    r = connection.execute(sa.text(
        "SELECT 1 FROM information_schema.tables WHERE table_name=:name"
    ), {"name": table})
    return r.scalar() is not None


def _column_exists(connection, table, column):
    if connection.dialect.name == 'sqlite':
        r = connection.execute(sa.text(
            f"SELECT 1 FROM pragma_table_info('{table}') WHERE name=:name"
        ), {"name": column})
        return r.scalar() is not None
    r = connection.execute(sa.text(
        "SELECT 1 FROM information_schema.columns WHERE table_name=:table AND column_name=:name"
    ), {"table": table, "name": column})
    return r.scalar() is not None


def upgrade():
    conn = op.get_bind()

    if not _table_exists(conn, 'tenants'):
        op.create_table(
            'tenants',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('name', sa.String(120), nullable=False),
            sa.Column('slug', sa.String(60), unique=True, nullable=False),
            sa.Column('plan', sa.String(20), server_default='starter'),
            sa.Column('is_active', sa.Boolean(), server_default='1'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
        )
        op.execute("INSERT INTO tenants (name, slug, plan, is_active) VALUES ('Empresa Demo', 'default', 'starter', 1)")

    if not _table_exists(conn, 'warehouses'):
        op.create_table(
            'warehouses',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
            sa.Column('code', sa.String(20), nullable=False),
            sa.Column('name', sa.String(120), nullable=False),
            sa.Column('city', sa.String(80), nullable=True),
            sa.Column('address', sa.String(255), nullable=True),
            sa.Column('is_default', sa.Boolean(), server_default='0'),
            sa.Column('is_active', sa.Boolean(), server_default='1'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
        )
        op.execute(
            "INSERT INTO warehouses (tenant_id, code, name, city, is_default, is_active) "
            "VALUES (1, 'MAIN', 'Almacén Principal', 'Málaga', 1, 1)"
        )

    tenant_cols = [
        ('users', 'tenant_id'),
        ('stock', 'tenant_id'),
        ('stock', 'warehouse_id'),
        ('suppliers', 'tenant_id'),
        ('purchase_orders', 'tenant_id'),
        ('item_requests', 'tenant_id'),
    ]
    for table, col in tenant_cols:
        if not _column_exists(conn, table, col):
            if conn.dialect.name == 'sqlite':
                op.execute(f"ALTER TABLE {table} ADD COLUMN {col} INTEGER")
            else:
                op.add_column(table, sa.Column(col, sa.Integer(), nullable=True))

    if not _column_exists(conn, 'item_requests', 'signature_data'):
        if conn.dialect.name == 'sqlite':
            op.execute("ALTER TABLE item_requests ADD COLUMN signature_data TEXT")
        else:
            op.add_column('item_requests', sa.Column('signature_data', sa.Text(), nullable=True))

    if not _table_exists(conn, 'warehouse_transfers'):
        op.create_table(
            'warehouse_transfers',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
            sa.Column('stock_id', sa.Integer(), sa.ForeignKey('stock.id'), nullable=False),
            sa.Column('from_warehouse_id', sa.Integer(), sa.ForeignKey('warehouses.id'), nullable=False),
            sa.Column('to_warehouse_id', sa.Integer(), sa.ForeignKey('warehouses.id'), nullable=False),
            sa.Column('quantity', sa.Integer(), nullable=False),
            sa.Column('status', sa.String(20), server_default='pendiente'),
            sa.Column('requested_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('completed_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('completed_at', sa.DateTime(), nullable=True),
        )

    # Backfill tenant_id = 1
    for table in ('users', 'stock', 'suppliers', 'purchase_orders', 'item_requests'):
        if _column_exists(conn, table, 'tenant_id'):
            op.execute(f"UPDATE {table} SET tenant_id = 1 WHERE tenant_id IS NULL")


def downgrade():
    pass
