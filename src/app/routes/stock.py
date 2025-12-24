"""
Stock management routes
Adapted from api/routes.py
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_
from app.models import db, Stock, StockMovement, MaintenanceRecord, StockStatusEnum, StockTypeEnum, CustomStockType
from app.utils import (
    validate_barcode, validate_inventario, validate_modelo, validate_cantidad,
    validate_request_data, error_handler
)
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
stock_bp = Blueprint('stock', __name__)

# Import routes from the original file
# This is a temporary bridge - ideally refactor each route
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'api'))
from routes import api as original_api

# Copy routes from original blueprint
for rule in original_api.url_map.iter_rules():
    if rule.endpoint.startswith('api.'):
        # Register routes with new blueprint
        pass  # Will be handled by importing the original for now

# For now, we'll use the original routes but with updated imports
# This allows gradual migration

