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
        print(f"Converting user to dict: {self.username}, type: {self.user_type}")  # Debug log
        user_type_value = self.user_type.value if isinstance(self.user_type, UserTypeEnum) else self.user_type
        print(f"User type value: {user_type_value}")  # Debug log
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
    barcode = db.Column(db.String(50), unique=True, nullable=False)
    inventario = db.Column(db.String(50), nullable=False)
    dispositivo = db.Column(db.Enum(StockTypeEnum), nullable=False)
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    image_url = db.Column(db.String(200))

    # Relaciones
    movements = db.relationship('StockMovement', back_populates='stock')
    maintenance_records = db.relationship('MaintenanceRecord', back_populates='stock')

    __table_args__ = (
        Index('idx_stock_barcode', 'barcode'),
        Index('idx_stock_status', 'status'),
        Index('idx_stock_type', 'stocktype'),
    )

    def __repr__(self):
        return f'<Stock {self.barcode}>'

# Modelo de Movimiento de Stock
class StockMovement(db.Model):
    __tablename__ = 'stock_movements'
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
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
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
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

@event.listens_for(Stock, 'before_update')
def stock_before_update(mapper, connection, target):
    target.updated_at = datetime.utcnow()

@event.listens_for(StockMovement, 'after_insert')
def update_stock_quantity(mapper, connection, target):
    stock = Stock.query.get(target.stock_id)
    if target.movement_type == 'entrada':
        stock.cantidad += target.quantity
    elif target.movement_type == 'salida':
        stock.cantidad -= target.quantity
    db.session.commit()

