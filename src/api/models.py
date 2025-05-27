# src/api/models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum, Index, event
from datetime import datetime, timedelta
import enum
import uuid

# Inicializa SQLAlchemy
db = SQLAlchemy()

# Enum para tipos de usuario
class UserTypeEnum(enum.Enum):
    admin = "admin"
    tecnico = "tecnico"
    usuario = "usuario"

# Enum para tipos de stock
class StockTypeEnum(enum.Enum):
    monitor = "monitor"
    teclado = "teclado"
    cable = "cable"
    mouse = "mouse"
    camara = "camara"
    otro = "otro"

# Enum para estados de stock
class StockStatusEnum(enum.Enum):
    disponible = "disponible"
    asignado = "asignado"
    mantenimiento = "mantenimiento"
    baja = "baja"

# Modelo de Usuario
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), unique=True, nullable=False)
    firstName = db.Column(db.String(20), nullable=False)
    lastName = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    isActive = db.Column(db.Boolean, default=True, nullable=False)
    usertype = db.Column(db.Enum(UserTypeEnum), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def __repr__(self):
        return f'<User {self.email}>'

# Modelo de Stock
class Stock(db.Model):
    __tablename__ = 'stock'
    id = db.Column(db.Integer, primary_key=True)
    barcode = db.Column(db.String(100), unique=True, nullable=False)
    inventario = db.Column(db.String(100), nullable=False)
    dispositivo = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(250))
    cantidad = db.Column(db.Integer, default=1, nullable=False)
    stocktype = db.Column(db.Enum(StockTypeEnum), nullable=False)
    status = db.Column(db.Enum(StockStatusEnum), default=StockStatusEnum.disponible, nullable=False)
    location = db.Column(db.String(100))
    serial_number = db.Column(db.String(100), unique=True)
    purchase_date = db.Column(db.Date)
    warranty_expiry = db.Column(db.Date)
    last_maintenance = db.Column(db.DateTime)
    next_maintenance = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    image_url = db.Column(db.String(250))

    # Relaciones
    movements = db.relationship('StockMovement', back_populates='stock')
    maintenance_records = db.relationship('MaintenanceRecord', back_populates='stock')

    __table_args__ = (
        Index('idx_stock_barcode', 'barcode'),
        Index('idx_stock_status', 'status'),
        Index('idx_stock_type', 'stocktype'),
    )

    def __repr__(self):
        return f'<Stock {self.inventario} ({self.barcode})>'

# Modelo de Movimiento de Stock
class StockMovement(db.Model):
    __tablename__ = 'stock_movements'
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)  # entrada, salida, transferencia
    from_location = db.Column(db.String(100))
    to_location = db.Column(db.String(100))
    notes = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

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
    description = db.Column(db.Text, nullable=False)
    cost = db.Column(db.Numeric(10, 2))
    date_performed = db.Column(db.DateTime, default=datetime.utcnow)
    next_maintenance = db.Column(db.DateTime)
    status = db.Column(db.String(20), nullable=False)  # pendiente, en_proceso, completado
    
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
    __tablename__ = 'form'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_relationship = db.relationship("User")
    detailform_relationship = db.relationship("DetailForm", back_populates='form')

    def __repr__(self):
        return f'<Form {self.id}>'

# Modelo de Detalle del Formulario
class DetailForm(db.Model):
    __tablename__ = 'detailForm'
    id = db.Column(db.Integer, primary_key=True)
    formId = db.Column(db.Integer, db.ForeignKey('form.id'), nullable=False)
    form = db.relationship("Form", back_populates='detailform_relationship')
    stockId = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
    stock_relationship = db.relationship("Stock")
    description = db.Column(db.String(30), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    stocktype = db.Column(db.Enum(StockTypeEnum), nullable=False)
    initialDate = db.Column(db.Date, nullable=False)
    finalDate = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f'<DetailForm {self.id}>'

# Modelo de Usuario con UUID
class UserUUID(db.Model):
    __tablename__ = 'user_uuid'
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uuid = db.Column(db.String(36), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

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

