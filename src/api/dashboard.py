"""Dashboard ejecutivo y alertas."""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from .utils import role_required
from .services.dashboard_service import DashboardService, _active_stock_query
from .models import Stock, StockBatch, StockMovement
from .tenant_utils import get_current_tenant_id, scope_tenant

dashboard = Blueprint('dashboard', __name__)


@dashboard.route('/executive', methods=['GET'])
@jwt_required()
@role_required('admin')
def executive_dashboard():
    return jsonify(DashboardService.get_executive_summary()), 200


@dashboard.route('/expiration-alerts', methods=['GET'])
@jwt_required()
@role_required('admin')
def expiration_alerts():
    return jsonify(DashboardService.get_expiration_alerts()), 200


@dashboard.route('/low-stock', methods=['GET'])
@jwt_required()
@role_required('admin')
def low_stock():
    items = []
    for s in _active_stock_query().all():
        if s.stock_level() in ('bajo', 'critico'):
            items.append(s.to_summary_dict())
    items.sort(key=lambda x: (0 if x.get('stock_level') == 'critico' else 1, x.get('cantidad', 0)))
    return jsonify({'items': items, 'total': len(items)}), 200


@dashboard.route('/batches/<batch_number>/trace', methods=['GET'])
@jwt_required()
@role_required('admin')
def trace_batch(batch_number):
    """Trazabilidad por lote: stock, movimientos relacionados."""
    tid = get_current_tenant_id()
    batch_q = StockBatch.query.filter_by(batch_number=batch_number)
    stock_q = Stock.query.filter_by(batch_number=batch_number, deleted_at=None)
    if tid is not None:
        batch_q = batch_q.join(Stock).filter(Stock.tenant_id == tid)
        stock_q = stock_q.filter(Stock.tenant_id == tid)
    batches = batch_q.all()
    stocks = stock_q.all()
    stock_ids = {b.stock_id for b in batches} | {s.id for s in stocks}
    movements = []
    if stock_ids:
        movements = StockMovement.query.filter(StockMovement.stock_id.in_(stock_ids)).order_by(
            StockMovement.timestamp.desc()
        ).limit(200).all()
    return jsonify({
        'batch_number': batch_number,
        'batches': [b.to_dict() for b in batches],
        'stocks': [s.to_summary_dict() for s in stocks],
        'movements': [{
            'stock_id': m.stock_id,
            'type': m.movement_type,
            'quantity': m.quantity,
            'timestamp': m.timestamp.isoformat(),
            'notes': m.notes,
        } for m in movements],
    }), 200
