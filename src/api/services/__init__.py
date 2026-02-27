# Capa de servicios: lógica de negocio separada de las rutas
from .auth_service import AuthService
from .stock_service import StockService

__all__ = ['AuthService', 'StockService']
