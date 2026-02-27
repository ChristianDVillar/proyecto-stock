# Capa de acceso a datos: solo queries y persistencia.
# La lógica de negocio vive en services/.
from .stock_repository import StockRepository

__all__ = ['StockRepository']
