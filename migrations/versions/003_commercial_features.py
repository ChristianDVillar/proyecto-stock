"""Commercial features: suppliers, purchase orders, stock extensions.

Revision ID: 003_commercial
Revises: 002_add_stock
Create Date: 2026-03-03
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))

from alembic import op
import sqlalchemy as sa

revision = '003_commercial'
down_revision = '002_add_stock'
branch_labels = None
depends_on = None


def _column_exists(connection, table, column):
    dialect = connection.dialect.name
    if dialect == 'sqlite':
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


def _table_exists(connection, table):
    dialect = connection.dialect.name
    if dialect == 'sqlite':
        r = connection.execute(sa.text(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=:name"
        ), {"name": table})
        return r.scalar() is not None
    r = connection.execute(sa.text(
        "SELECT 1 FROM information_schema.tables WHERE table_name=:name"
    ), {"name": table})
    return r.scalar() is not None


def upgrade():
    connection = op.get_bind()

    if not _table_exists(connection, 'suppliers'):
        op.create_table(
            'suppliers',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('name', sa.String(120), nullable=False),
            sa.Column('tax_id', sa.String(30), nullable=True),
            sa.Column('phone', sa.String(30), nullable=True),
            sa.Column('email', sa.String(120), nullable=True),
            sa.Column('address', sa.String(255), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
        )
        op.create_index('ix_suppliers_name', 'suppliers', ['name'])

    stock_cols = [
        ('expiration_date', sa.Date()),
        ('batch_number', sa.String(50)),
        ('supplier_id', sa.Integer()),
        ('minimum_stock', sa.Integer()),
        ('optimal_stock', sa.Integer()),
        ('unit_cost', sa.Float()),
        ('contains_gluten', sa.Boolean()),
        ('contains_milk', sa.Boolean()),
        ('contains_nuts', sa.Boolean()),
        ('contains_soy', sa.Boolean()),
        ('mac_address', sa.String(50)),
        ('hostname', sa.String(100)),
        ('assigned_user_id', sa.Integer()),
    ]
    for col_name, col_type in stock_cols:
        if not _column_exists(connection, 'stock', col_name):
            if connection.dialect.name == 'sqlite':
                if isinstance(col_type, sa.Boolean):
                    op.execute(f"ALTER TABLE stock ADD COLUMN {col_name} BOOLEAN DEFAULT 0")
                elif isinstance(col_type, sa.Integer):
                    op.execute(f"ALTER TABLE stock ADD COLUMN {col_name} INTEGER")
                elif isinstance(col_type, sa.Float):
                    op.execute(f"ALTER TABLE stock ADD COLUMN {col_name} REAL")
                elif isinstance(col_type, sa.Date):
                    op.execute(f"ALTER TABLE stock ADD COLUMN {col_name} DATE")
                else:
                    op.execute(f"ALTER TABLE stock ADD COLUMN {col_name} VARCHAR(50)")
            else:
                kwargs = {'nullable': True}
                if isinstance(col_type, sa.Boolean):
                    kwargs['server_default'] = 'false'
                op.add_column('stock', sa.Column(col_name, col_type, **kwargs))

    if not _table_exists(connection, 'stock_batches'):
        op.create_table(
            'stock_batches',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('stock_id', sa.Integer(), sa.ForeignKey('stock.id', ondelete='CASCADE'), nullable=False),
            sa.Column('batch_number', sa.String(50), nullable=False),
            sa.Column('quantity', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('expiration_date', sa.Date(), nullable=True),
            sa.Column('supplier_id', sa.Integer(), sa.ForeignKey('suppliers.id'), nullable=True),
            sa.Column('received_at', sa.DateTime(), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
        )
        op.create_index('idx_batch_number', 'stock_batches', ['batch_number'])

    if not _table_exists(connection, 'asset_events'):
        op.create_table(
            'asset_events',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('stock_id', sa.Integer(), sa.ForeignKey('stock.id', ondelete='CASCADE'), nullable=False),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
            sa.Column('event_type', sa.String(20), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('metadata_json', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
        )

    if not _table_exists(connection, 'purchase_orders'):
        op.create_table(
            'purchase_orders',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('order_number', sa.String(30), unique=True, nullable=False),
            sa.Column('supplier_id', sa.Integer(), sa.ForeignKey('suppliers.id'), nullable=False),
            sa.Column('status', sa.String(20), nullable=False, server_default='borrador'),
            sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('approved_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
            sa.Column('approved_at', sa.DateTime(), nullable=True),
            sa.Column('received_at', sa.DateTime(), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('total_amount', sa.Float(), server_default='0'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
        )
        op.create_index('ix_purchase_orders_order_number', 'purchase_orders', ['order_number'])

    if not _table_exists(connection, 'purchase_order_lines'):
        op.create_table(
            'purchase_order_lines',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('purchase_order_id', sa.Integer(), sa.ForeignKey('purchase_orders.id', ondelete='CASCADE'), nullable=False),
            sa.Column('stock_id', sa.Integer(), sa.ForeignKey('stock.id', ondelete='SET NULL'), nullable=True),
            sa.Column('description', sa.String(200), nullable=False),
            sa.Column('quantity_ordered', sa.Integer(), nullable=False),
            sa.Column('quantity_received', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('unit_cost', sa.Float(), nullable=True),
            sa.Column('barcode', sa.String(50), nullable=True),
        )


def downgrade():
    for table in ('purchase_order_lines', 'purchase_orders', 'asset_events', 'stock_batches', 'suppliers'):
        if op.get_bind().dialect.name != 'sqlite':
            op.drop_table(table)
