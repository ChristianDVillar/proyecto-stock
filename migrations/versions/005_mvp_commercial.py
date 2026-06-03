"""MVP comercial: costes, ubicaciones, alertas, inventario cíclico, API keys.

Revision ID: 005_mvp_commercial
Revises: 004_saas_warehouse
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))

from alembic import op
import sqlalchemy as sa

revision = '005_mvp_commercial'
down_revision = '004_saas_warehouse'
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


def _add_col(conn, table, col, sql_type, default=None):
    if not _column_exists(conn, table, col):
        if conn.dialect.name == 'sqlite':
            default_clause = f" DEFAULT {default}" if default is not None else ''
            op.execute(f"ALTER TABLE {table} ADD COLUMN {col} {sql_type}{default_clause}")
        else:
            op.add_column(table, sa.Column(col, sql_type, nullable=True))


def upgrade():
    conn = op.get_bind()

    stock_cols = [
        ('purchase_price', 'FLOAT', None),
        ('sale_price', 'FLOAT', None),
        ('average_cost', 'FLOAT', None),
        ('location_code', 'VARCHAR(20)', None),
        ('location_aisle', 'VARCHAR(10)', None),
        ('location_shelf', 'VARCHAR(10)', None),
        ('public_token', 'VARCHAR(36)', None),
        ('qr_public_enabled', 'BOOLEAN', '0'),
        ('manual_pdf_url', 'VARCHAR(500)', None),
        ('menu_item_name', 'VARCHAR(120)', None),
        ('is_menu_ingredient', 'BOOLEAN', '0'),
    ]
    for col, typ, default in stock_cols:
        _add_col(conn, 'stock', col, typ, default)

    # purchase_price backfill from unit_cost
    if _column_exists(conn, 'stock', 'purchase_price') and _column_exists(conn, 'stock', 'unit_cost'):
        op.execute("UPDATE stock SET purchase_price = unit_cost WHERE purchase_price IS NULL AND unit_cost IS NOT NULL")
        op.execute("UPDATE stock SET average_cost = unit_cost WHERE average_cost IS NULL AND unit_cost IS NOT NULL")

    if not _table_exists(conn, 'alert_configs'):
        op.create_table(
            'alert_configs',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
            sa.Column('channel', sa.String(20), nullable=False),
            sa.Column('event_type', sa.String(30), nullable=False),
            sa.Column('enabled', sa.Boolean(), server_default='1'),
            sa.Column('destination', sa.String(500), nullable=True),
            sa.Column('extra_config', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
        )

    if not _table_exists(conn, 'cyclic_inventory_schedules'):
        op.create_table(
            'cyclic_inventory_schedules',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
            sa.Column('name', sa.String(120), nullable=False),
            sa.Column('weekday', sa.Integer(), nullable=False),
            sa.Column('device_type', sa.String(50), nullable=True),
            sa.Column('warehouse_id', sa.Integer(), sa.ForeignKey('warehouses.id'), nullable=True),
            sa.Column('is_active', sa.Boolean(), server_default='1'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
        )

    if not _table_exists(conn, 'cyclic_inventory_tasks'):
        op.create_table(
            'cyclic_inventory_tasks',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
            sa.Column('schedule_id', sa.Integer(), sa.ForeignKey('cyclic_inventory_schedules.id'), nullable=True),
            sa.Column('title', sa.String(200), nullable=False),
            sa.Column('status', sa.String(20), server_default='pendiente'),
            sa.Column('due_date', sa.Date(), nullable=False),
            sa.Column('assigned_to', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
            sa.Column('completed_at', sa.DateTime(), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
        )

    if not _table_exists(conn, 'api_keys'):
        op.create_table(
            'api_keys',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
            sa.Column('name', sa.String(120), nullable=False),
            sa.Column('key_prefix', sa.String(12), nullable=False),
            sa.Column('key_hash', sa.String(128), nullable=False),
            sa.Column('is_active', sa.Boolean(), server_default='1'),
            sa.Column('scopes', sa.String(200), server_default='read,write'),
            sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
            sa.Column('last_used_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
        )

    if not _table_exists(conn, 'webhooks'):
        op.create_table(
            'webhooks',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id'), nullable=False),
            sa.Column('url', sa.String(500), nullable=False),
            sa.Column('secret', sa.String(64), nullable=True),
            sa.Column('events', sa.String(300), server_default='stock.updated,order.approved'),
            sa.Column('is_active', sa.Boolean(), server_default='1'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
        )


def downgrade():
    pass
