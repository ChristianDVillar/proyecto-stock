# src/api/models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum, Index, event, String
from datetime import datetime, timedelta
import enum
import uuid
from flask_login import UserMixin

# Inicializa SQLAlchemy
db = SQLAlchemy()

# Enum para tipos de usuario
class UserTypeEnum(enum.Enum):
    admin = 'admin'
    user = 'user'

    def __str__(self):
        return self.value

# Enum para tipos de dispositivos
class DeviceTypeEnum(enum.Enum):
    computadora = 'computadora'
    impresora = 'impresora'
    monitor = 'monitor'
    teclado = 'teclado'
    mouse = 'mouse'
    router = 'router'
    switch = 'switch'
    servidor = 'servidor'
    laptop = 'laptop'
    tablet = 'tablet'
    smartphone = 'smartphone'
    otro = 'otro'

# Modelo para tipos de dispositivos personalizados
class CustomDeviceType(db.Model):
    __tablename__ = 'custom_device_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<CustomDeviceType {self.name}>'

# Enum para tipos de stock
class StockTypeEnum(enum.Enum):
    computadora = 'computadora'
    impresora = 'impresora'
    monitor = 'monitor'
    teclado = 'teclado'
    mouse = 'mouse'
    router = 'router'
    switch = 'switch'
    servidor = 'servidor'
    laptop = 'laptop'
    tablet = 'tablet'
    smartphone = 'smartphone'
    otro = 'otro'

# Modelo para tipos de stock personalizados
class CustomStockType(db.Model):
    __tablename__ = 'custom_stock_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f'<CustomStockType {self.name}>'

# Enum para estados de stock
class StockStatusEnum(enum.Enum):
    disponible = 'disponible'
    en_uso = 'en_uso'
    mantenimiento = 'mantenimiento'
    baja = 'baja'


class PurchaseOrderStatusEnum(enum.Enum):
    borrador = 'borrador'
    pendiente = 'pendiente'
    aprobada = 'aprobada'
    recibida = 'recibida'
    cancelada = 'cancelada'


class AssetEventTypeEnum(enum.Enum):
    comprado = 'comprado'
    asignado = 'asignado'
    mantenimiento = 'mantenimiento'
    reparacion = 'reparacion'
    reasignado = 'reasignado'
    baja = 'baja'
    transferencia = 'transferencia'


class TransferStatusEnum(enum.Enum):
    pendiente = 'pendiente'
    completada = 'completada'
    cancelada = 'cancelada'


class TenantPlanEnum(enum.Enum):
    starter = 'starter'
    pro = 'pro'
    business = 'business'


# Multi-tenant (SaaS)
class Tenant(db.Model):
    __tablename__ = 'tenants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(60), unique=True, nullable=False, index=True)
    plan = db.Column(db.Enum(TenantPlanEnum), default=TenantPlanEnum.starter, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship('User', backref='tenant', lazy='dynamic')
    warehouses = db.relationship('Warehouse', backref='tenant', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'plan': self.plan.value if hasattr(self.plan, 'value') else str(self.plan),
            'is_active': self.is_active,
        }


class Warehouse(db.Model):
    __tablename__ = 'warehouses'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    code = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(80), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    is_default = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (Index('idx_warehouse_tenant_code', 'tenant_id', 'code', unique=True),)

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'code': self.code,
            'name': self.name,
            'city': self.city,
            'address': self.address,
            'is_default': self.is_default,
            'is_active': self.is_active,
        }


class WarehouseTransfer(db.Model):
    __tablename__ = 'warehouse_transfers'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id', ondelete='CASCADE'), nullable=False)
    from_warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    to_warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(TransferStatusEnum), default=TransferStatusEnum.pendiente, nullable=False)
    requested_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    completed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    stock = db.relationship('Stock', foreign_keys=[stock_id])
    from_warehouse = db.relationship('Warehouse', foreign_keys=[from_warehouse_id])
    to_warehouse = db.relationship('Warehouse', foreign_keys=[to_warehouse_id])

    def to_dict(self):
        return {
            'id': self.id,
            'stock_id': self.stock_id,
            'stock_barcode': self.stock.barcode if self.stock else None,
            'from_warehouse_id': self.from_warehouse_id,
            'from_warehouse_name': self.from_warehouse.name if self.from_warehouse else None,
            'to_warehouse_id': self.to_warehouse_id,
            'to_warehouse_name': self.to_warehouse.name if self.to_warehouse else None,
            'quantity': self.quantity,
            'status': self.status.value if hasattr(self.status, 'value') else str(self.status),
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }


# Proveedor
class Supplier(db.Model):
    __tablename__ = 'suppliers'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    tax_id = db.Column(db.String(30), nullable=True)  # CIF/NIF
    phone = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    stocks = db.relationship('Stock', back_populates='supplier', lazy='dynamic')
    purchase_orders = db.relationship('PurchaseOrder', back_populates='supplier', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'tax_id': self.tax_id,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'notes': self.notes,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

# Modelo de Usuario
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True)
    username = db.Column(db.String(80), nullable=False, index=True)
    password = db.Column(db.String(120), nullable=False)
    user_type = db.Column(db.Enum(UserTypeEnum), nullable=False, default=UserTypeEnum.user)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    __table_args__ = (Index('idx_user_tenant_username', 'tenant_id', 'username', unique=True),)
    
    # Relaciones
    forms = db.relationship('Form', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        user_type_value = self.user_type.value if isinstance(self.user_type, UserTypeEnum) else self.user_type
        return {
            'id': self.id,
            'username': self.username,
            'user_type': user_type_value,
            'tenant_id': self.tenant_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Modelo de Stock
class Stock(db.Model):
    __tablename__ = 'stock'

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=True, index=True)
    barcode = db.Column(db.String(50), nullable=False, index=True)
    inventario = db.Column(db.String(50), nullable=False, index=True)
    dispositivo = db.Column(db.Enum(StockTypeEnum), nullable=False, index=True)
    modelo = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(200))
    cantidad = db.Column(db.Integer, default=1)
    stocktype = db.Column(db.Enum(StockTypeEnum), default=StockTypeEnum.computadora)
    status = db.Column(db.Enum(StockStatusEnum), default=StockStatusEnum.disponible)
    location = db.Column(db.String(50), default='default')
    serial_number = db.Column(db.String(50))
    purchase_date = db.Column(db.Date)
    warranty_expiry = db.Column(db.Date)
    last_maintenance = db.Column(db.DateTime)
    next_maintenance = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    image_url = db.Column(db.String(200))
    deleted_at = db.Column(db.DateTime, nullable=True)  # soft delete
    # Control de concurrencia optimista: se incrementa en cada actualización
    version = db.Column(db.Integer, nullable=False, default=1)

    # Comercial: vencimientos, lotes, proveedor, reposición
    expiration_date = db.Column(db.Date, nullable=True, index=True)
    batch_number = db.Column(db.String(50), nullable=True, index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    minimum_stock = db.Column(db.Integer, nullable=True, default=0)
    optimal_stock = db.Column(db.Integer, nullable=True)
    unit_cost = db.Column(db.Float, nullable=True)

    # Alérgenos (restauración / carta digital)
    contains_gluten = db.Column(db.Boolean, default=False, nullable=False)
    contains_milk = db.Column(db.Boolean, default=False, nullable=False)
    contains_nuts = db.Column(db.Boolean, default=False, nullable=False)
    contains_soy = db.Column(db.Boolean, default=False, nullable=False)

    # Activos IT
    mac_address = db.Column(db.String(50), nullable=True)
    hostname = db.Column(db.String(100), nullable=True)
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # Relaciones (CASCADE en hijos: al borrar stock se borran movimientos y mantenimientos)
    supplier = db.relationship('Supplier', back_populates='stocks')
    assigned_user = db.relationship('User', foreign_keys=[assigned_user_id])
    movements = db.relationship('StockMovement', back_populates='stock', passive_deletes=True)
    maintenance_records = db.relationship('MaintenanceRecord', back_populates='stock', passive_deletes=True)
    asset_events = db.relationship('AssetEvent', back_populates='stock', passive_deletes=True, lazy='dynamic')
    batches = db.relationship('StockBatch', back_populates='stock', passive_deletes=True, lazy='dynamic')
    warehouse = db.relationship('Warehouse', foreign_keys=[warehouse_id])

    __table_args__ = (
        Index('idx_stock_tenant_barcode', 'tenant_id', 'barcode', unique=True),
        Index('idx_stock_status', 'status'),
        Index('idx_stock_type', 'stocktype'),
        Index('idx_stock_created_at', 'created_at'),
        Index('idx_stock_deleted_at', 'deleted_at'),
        Index('idx_stock_version', 'id', 'version'),
    )

    def __repr__(self):
        return f'<Stock {self.barcode}>'

    def stock_level(self):
        """Indicador de reposición: normal | bajo | critico."""
        min_s = self.minimum_stock if self.minimum_stock is not None else 0
        opt = self.optimal_stock
        qty = self.cantidad or 0
        if min_s > 0 and qty < min_s:
            return 'critico'
        if opt is not None and qty < opt:
            return 'bajo'
        return 'normal'

    def days_until_expiration(self):
        if not self.expiration_date:
            return None
        return (self.expiration_date - datetime.utcnow().date()).days

    def expiration_alert(self):
        """None | vencido | 7_dias | 30_dias | 90_dias"""
        days = self.days_until_expiration()
        if days is None:
            return None
        if days < 0:
            return 'vencido'
        if days <= 7:
            return '7_dias'
        if days <= 30:
            return '30_dias'
        if days <= 90:
            return '90_dias'
        return None

    def warranty_days_remaining(self):
        if not self.warranty_expiry:
            return None
        return (self.warranty_expiry - datetime.utcnow().date()).days

    def to_summary_dict(self):
        """Resumen para listados y dashboard."""
        supplier_name = self.supplier.name if self.supplier else None
        assigned = self.assigned_user.username if self.assigned_user else None
        return {
            'id': self.id,
            'barcode': self.barcode,
            'inventario': self.inventario,
            'dispositivo': self.dispositivo.value if hasattr(self.dispositivo, 'value') else str(self.dispositivo),
            'modelo': self.modelo,
            'descripcion': self.descripcion,
            'cantidad': self.cantidad,
            'status': self.status.value if hasattr(self.status, 'value') else str(self.status),
            'location': self.location,
            'warehouse_id': self.warehouse_id,
            'warehouse_name': self.warehouse.name if self.warehouse else None,
            'tenant_id': self.tenant_id,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'batch_number': self.batch_number,
            'supplier_id': self.supplier_id,
            'supplier_name': supplier_name,
            'minimum_stock': self.minimum_stock,
            'optimal_stock': self.optimal_stock,
            'stock_level': self.stock_level(),
            'unit_cost': self.unit_cost,
            'expiration_alert': self.expiration_alert(),
            'days_until_expiration': self.days_until_expiration(),
            'warranty_days_remaining': self.warranty_days_remaining(),
            'serial_number': self.serial_number,
            'mac_address': self.mac_address,
            'hostname': self.hostname,
            'assigned_user_id': self.assigned_user_id,
            'assigned_user': assigned,
            'contains_gluten': self.contains_gluten,
            'contains_milk': self.contains_milk,
            'contains_nuts': self.contains_nuts,
            'contains_soy': self.contains_soy,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'warranty_expiry': self.warranty_expiry.isoformat() if self.warranty_expiry else None,
            'last_maintenance': self.last_maintenance.isoformat() if self.last_maintenance else None,
            'next_maintenance': self.next_maintenance.isoformat() if self.next_maintenance else None,
            'image_url': self.image_url,
            'stocktype': self.stocktype.value if hasattr(self.stocktype, 'value') else str(self.stocktype),
        }

# Modelo de Movimiento de Stock
class StockMovement(db.Model):
    __tablename__ = 'stock_movements'
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)  # entrada/salida
    from_location = db.Column(db.String(100))
    to_location = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

    # Relaciones
    stock = db.relationship('Stock', back_populates='movements')
    user = db.relationship('User')

    __table_args__ = (
        Index('idx_movement_stock', 'stock_id'),
        Index('idx_movement_date', 'timestamp'),
    )

# Modelo de Registro de Mantenimiento
class MaintenanceRecord(db.Model):
    __tablename__ = 'maintenance_records'
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id', ondelete='CASCADE'), nullable=False)
    technician_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    maintenance_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    date_performed = db.Column(db.DateTime, default=datetime.utcnow)
    next_maintenance = db.Column(db.DateTime)
    cost = db.Column(db.Float)
    status = db.Column(db.String(20))  # pendiente/en_proceso/completado
    
    # Relaciones
    stock = db.relationship('Stock', back_populates='maintenance_records')
    technician = db.relationship('User')

    __table_args__ = (
        Index('idx_maintenance_stock', 'stock_id'),
        Index('idx_maintenance_date', 'date_performed'),
    )


# Modelo de historial de cambios (auditoría)
class StockHistory(db.Model):
    __tablename__ = 'stock_history'
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id', ondelete='CASCADE'), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(20), nullable=False)  # create, update, delete, soft_delete
    old_value = db.Column(db.Text)  # JSON snapshot anterior
    new_value = db.Column(db.Text)  # JSON snapshot nuevo
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_stock_history_stock', 'stock_id'),
        Index('idx_stock_history_date', 'timestamp'),
    )


# Modelo de Sesión de Usuario
class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    user_agent = db.Column(db.String(200))
    ip_address = db.Column(db.String(45))

    # Relación
    user = db.relationship('User')

    __table_args__ = (
        Index('idx_session_user', 'user_id'),
        Index('idx_session_token', 'session_id'),
    )

    def is_expired(self):
        return datetime.utcnow() > self.expires_at

# Modelo de Formulario
class Form(db.Model):
    __tablename__ = 'forms'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    details = db.relationship("DetailForm", backref='form', lazy=True)

    def __repr__(self):
        return f'<Form {self.id}>'

# Modelo de Detalle del Formulario
class DetailForm(db.Model):
    __tablename__ = 'detail_forms'
    
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('forms.id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
    stock = db.relationship("Stock")
    description = db.Column(db.String(30), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    stocktype = db.Column(db.Enum(StockTypeEnum), nullable=False)
    initial_date = db.Column(db.Date, nullable=False)
    final_date = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f'<DetailForm {self.id}>'

# Modelo de Usuario con UUID
class UserUUID(db.Model):
    __tablename__ = 'user_uuid'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uuid = db.Column(db.String(36), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user = db.relationship('User', backref='uuids')

    def is_expired(self):
        expiration_time = self.created_at + timedelta(minutes=45)
        return datetime.utcnow() > expiration_time

    def __repr__(self):
        return f'<UserUUID {self.id}>'


# Solicitud de elementos (usuario, elemento/stock, fecha, tiempo, firma; admin: aprobar/rechazar, fecha entrega)
class ItemRequest(db.Model):
    __tablename__ = 'item_requests'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id', ondelete='SET NULL'), nullable=True)  # elemento solicitado
    request_username = db.Column(db.String(80), nullable=True)
    request_date = db.Column(db.Date, nullable=False)
    duration_type = db.Column(db.String(20), nullable=False)  # semanas | horas | definitivo
    duration_value = db.Column(db.Integer, nullable=True)
    signed = db.Column(db.Boolean, default=False, nullable=False)
    signed_at = db.Column(db.DateTime, nullable=True)
    signature_data = db.Column(db.Text, nullable=True)  # firma digital base64
    status = db.Column(db.String(20), default='pendiente', nullable=False)  # pendiente | aprobado | rechazado
    delivery_date = db.Column(db.Date, nullable=True)  # fecha de entrega (admin)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    requester = db.relationship('User', backref=db.backref('item_requests', lazy='dynamic'))
    stock = db.relationship('Stock', backref=db.backref('item_requests', lazy='dynamic'))
    __table_args__ = (Index('idx_item_request_user', 'user_id'), Index('idx_item_request_date', 'request_date'))


class StockBatch(db.Model):
    """Trazabilidad por lote."""
    __tablename__ = 'stock_batches'
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id', ondelete='CASCADE'), nullable=False)
    batch_number = db.Column(db.String(50), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    expiration_date = db.Column(db.Date, nullable=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)
    received_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)

    stock = db.relationship('Stock', back_populates='batches')
    supplier = db.relationship('Supplier')

    __table_args__ = (Index('idx_batch_number', 'batch_number'),)

    def to_dict(self):
        return {
            'id': self.id,
            'stock_id': self.stock_id,
            'batch_number': self.batch_number,
            'quantity': self.quantity,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'supplier_id': self.supplier_id,
            'received_at': self.received_at.isoformat() if self.received_at else None,
            'notes': self.notes,
        }


class AssetEvent(db.Model):
    """Historial del ciclo de vida del activo IT."""
    __tablename__ = 'asset_events'
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    event_type = db.Column(db.Enum(AssetEventTypeEnum), nullable=False)
    description = db.Column(db.Text, nullable=True)
    metadata_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    stock = db.relationship('Stock', back_populates='asset_events')
    user = db.relationship('User')

    def to_dict(self):
        return {
            'id': self.id,
            'stock_id': self.stock_id,
            'user_id': self.user_id,
            'event_type': self.event_type.value if hasattr(self.event_type, 'value') else str(self.event_type),
            'description': self.description,
            'metadata_json': self.metadata_json,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class PurchaseOrder(db.Model):
    __tablename__ = 'purchase_orders'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=True, index=True)
    order_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    status = db.Column(db.Enum(PurchaseOrderStatusEnum), default=PurchaseOrderStatusEnum.borrador, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    received_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    total_amount = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    supplier = db.relationship('Supplier', back_populates='purchase_orders')
    creator = db.relationship('User', foreign_keys=[created_by])
    approver = db.relationship('User', foreign_keys=[approved_by])
    lines = db.relationship('PurchaseOrderLine', back_populates='purchase_order', cascade='all, delete-orphan')

    def to_dict(self, include_lines=True):
        data = {
            'id': self.id,
            'order_number': self.order_number,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.name if self.supplier else None,
            'status': self.status.value if hasattr(self.status, 'value') else str(self.status),
            'created_by': self.created_by,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'received_at': self.received_at.isoformat() if self.received_at else None,
            'notes': self.notes,
            'total_amount': self.total_amount,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_lines:
            data['lines'] = [ln.to_dict() for ln in self.lines]
        return data


class PurchaseOrderLine(db.Model):
    __tablename__ = 'purchase_order_lines'
    id = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_orders.id', ondelete='CASCADE'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id', ondelete='SET NULL'), nullable=True)
    description = db.Column(db.String(200), nullable=False)
    quantity_ordered = db.Column(db.Integer, nullable=False)
    quantity_received = db.Column(db.Integer, default=0, nullable=False)
    unit_cost = db.Column(db.Float, nullable=True)
    barcode = db.Column(db.String(50), nullable=True)

    purchase_order = db.relationship('PurchaseOrder', back_populates='lines')
    stock = db.relationship('Stock')

    def to_dict(self):
        return {
            'id': self.id,
            'purchase_order_id': self.purchase_order_id,
            'stock_id': self.stock_id,
            'description': self.description,
            'quantity_ordered': self.quantity_ordered,
            'quantity_received': self.quantity_received,
            'unit_cost': self.unit_cost,
            'barcode': self.barcode,
            'line_total': (self.unit_cost or 0) * self.quantity_ordered,
        }


@event.listens_for(Stock, 'before_update')
def stock_before_update(mapper, connection, target):
    target.updated_at = datetime.utcnow()

@event.listens_for(StockMovement, 'after_insert')
def update_stock_quantity(mapper, connection, target):
    """Actualiza cantidad del stock; no hacer commit aquí (lo hace la transacción externa)."""
    from sqlalchemy.orm import Session
    session = Session.object_session(target)
    if session is None:
        return
    stock = session.get(Stock, target.stock_id)
    if not stock:
        return
    if target.movement_type == 'entrada':
        stock.cantidad += target.quantity
    elif target.movement_type == 'salida':
        stock.cantidad -= target.quantity
    # 'transferencia': solo trazabilidad, no cambia cantidad total

