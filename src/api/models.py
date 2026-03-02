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

# Modelo de Usuario
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    user_type = db.Column(db.Enum(UserTypeEnum), nullable=False, default=UserTypeEnum.user)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
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
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Modelo de Stock
class Stock(db.Model):
    __tablename__ = 'stock'

    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(50), unique=True, nullable=False, index=True)
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

    # Relaciones (CASCADE en hijos: al borrar stock se borran movimientos y mantenimientos)
    movements = db.relationship('StockMovement', back_populates='stock', passive_deletes=True)
    maintenance_records = db.relationship('MaintenanceRecord', back_populates='stock', passive_deletes=True)

    __table_args__ = (
        Index('idx_stock_barcode', 'barcode'),
        Index('idx_stock_status', 'status'),
        Index('idx_stock_type', 'stocktype'),
        Index('idx_stock_created_at', 'created_at'),
        Index('idx_stock_deleted_at', 'deleted_at'),
        Index('idx_stock_version', 'id', 'version'),
    )

    def __repr__(self):
        return f'<Stock {self.barcode}>'

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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id', ondelete='SET NULL'), nullable=True)  # elemento solicitado
    request_username = db.Column(db.String(80), nullable=True)
    request_date = db.Column(db.Date, nullable=False)
    duration_type = db.Column(db.String(20), nullable=False)  # semanas | horas | definitivo
    duration_value = db.Column(db.Integer, nullable=True)
    signed = db.Column(db.Boolean, default=False, nullable=False)
    signed_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='pendiente', nullable=False)  # pendiente | aprobado | rechazado
    delivery_date = db.Column(db.Date, nullable=True)  # fecha de entrega (admin)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    requester = db.relationship('User', backref=db.backref('item_requests', lazy='dynamic'))
    stock = db.relationship('Stock', backref=db.backref('item_requests', lazy='dynamic'))
    __table_args__ = (Index('idx_item_request_user', 'user_id'), Index('idx_item_request_date', 'request_date'))


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

