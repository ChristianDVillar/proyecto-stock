"""Endpoints públicos: QR producto, carta alérgenos (Dakinis)."""
from flask import Blueprint, jsonify
from .models import Stock, MaintenanceRecord, AssetEvent, StockMovement

public = Blueprint('public', __name__)


@public.route('/product/<token>', methods=['GET'])
def public_product(token):
    stock = Stock.query.filter_by(public_token=token, qr_public_enabled=True).filter(
        Stock.deleted_at.is_(None)
    ).first()
    if not stock:
        return jsonify({'error': 'Producto no encontrado o QR deshabilitado'}), 404
    events = AssetEvent.query.filter_by(stock_id=stock.id).order_by(
        AssetEvent.created_at.desc()
    ).limit(10).all()
    maintenance = MaintenanceRecord.query.filter_by(stock_id=stock.id).order_by(
        MaintenanceRecord.date_performed.desc()
    ).limit(5).all()
    return jsonify({
        'product': {
            'modelo': stock.modelo,
            'barcode': stock.barcode,
            'descripcion': stock.descripcion,
            'serial_number': stock.serial_number,
            'warranty_expiry': stock.warranty_expiry.isoformat() if stock.warranty_expiry else None,
            'warranty_days_remaining': stock.warranty_days_remaining(),
            'manual_pdf_url': stock.manual_pdf_url,
            'location_code': stock.location_code,
            'allergens': stock.allergen_labels(),
        },
        'maintenance': [
            {'type': m.maintenance_type, 'date': m.date_performed.isoformat(), 'status': m.status}
            for m in maintenance
        ],
        'recent_events': [e.to_dict() for e in events],
    }), 200


@public.route('/menu/<tenant_slug>', methods=['GET'])
def public_menu_allergens(tenant_slug):
    """Ingredientes con alérgenos para carta QR (integración Dakinis)."""
    from .models import Tenant
    tenant = Tenant.query.filter_by(slug=tenant_slug, is_active=True).first()
    if not tenant:
        return jsonify({'error': 'Tenant no encontrado'}), 404
    items = Stock.query.filter_by(
        tenant_id=tenant.id, is_menu_ingredient=True
    ).filter(Stock.deleted_at.is_(None)).all()
    return jsonify({
        'tenant': tenant.name,
        'ingredients': [
            {
                'id': s.id,
                'name': s.menu_item_name or s.modelo,
                'barcode': s.barcode,
                'allergens': s.allergen_labels(),
                'contains_gluten': s.contains_gluten,
                'contains_milk': s.contains_milk,
                'contains_nuts': s.contains_nuts,
                'contains_soy': s.contains_soy,
            }
            for s in items
        ],
    }), 200
