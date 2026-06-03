from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import db, User, UserTypeEnum, ItemRequest, Stock
from .utils import role_required

solicitudes = Blueprint('solicitudes', __name__)


def _current_user_or_401():
    user_id = get_jwt_identity()
    if not user_id:
        return None, 401
    try:
        user = User.query.get(int(user_id))
    except (TypeError, ValueError):
        return None, 401
    if not user:
        return None, 401
    return user, None


def _serialize_solicitud(r):
    out = {
        'id': r.id,
        'user_id': r.user_id,
        'request_username': r.request_username,
        'request_date': r.request_date.isoformat() if r.request_date else None,
        'duration_type': r.duration_type,
        'duration_value': r.duration_value,
        'signed': r.signed,
        'signed_at': r.signed_at.isoformat() if r.signed_at else None,
        'status': getattr(r, 'status', None) or 'pendiente',
        'delivery_date': r.delivery_date.isoformat() if getattr(r, 'delivery_date', None) else None,
        'created_at': r.created_at.isoformat() if r.created_at else None,
        'stock_id': r.stock_id if hasattr(r, 'stock_id') else None,
    }
    if getattr(r, 'stock', None) and r.stock:
        out['stock'] = {
            'id': r.stock.id,
            'barcode': r.stock.barcode,
            'inventario': r.stock.inventario,
            'dispositivo': r.stock.dispositivo.value if hasattr(r.stock.dispositivo, 'value') else str(r.stock.dispositivo),
            'modelo': r.stock.modelo,
        }
    else:
        out['stock'] = None
    return out


@solicitudes.route('', methods=['GET'])
@jwt_required()
def list_solicitudes():
    user, err = _current_user_or_401()
    if err:
        return jsonify({'error': 'No autorizado'}), err
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        per_page = max(1, per_page)
        q = ItemRequest.query.order_by(ItemRequest.created_at.desc())
        if user.user_type != UserTypeEnum.admin:
            q = q.filter_by(user_id=user.id)
        pagination = q.paginate(page=page, per_page=per_page, error_out=False)
        items = [_serialize_solicitud(r) for r in pagination.items]
        total = pagination.total
        pages = pagination.pages or 1
        return jsonify({
            'items': items,
            'solicitudes': items,
            'total': total,
            'page': page,
            'pages': pages,
            'per_page': per_page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@solicitudes.route('', methods=['POST'])
@jwt_required()
def create_solicitud():
    user, err = _current_user_or_401()
    if err:
        return jsonify({'error': 'No autorizado'}), err
    try:
        data = request.get_json() or {}
        request_date = data.get('request_date')
        if not request_date:
            return jsonify({'error': 'Falta request_date (YYYY-MM-DD)'}), 400
        try:
            req_date = datetime.strptime(request_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'request_date debe ser YYYY-MM-DD'}), 400
        duration_type = (data.get('duration_type') or '').strip().lower()
        if duration_type not in ('semanas', 'horas', 'definitivo'):
            return jsonify({'error': 'duration_type debe ser: semanas, horas o definitivo'}), 400
        duration_value = None
        if duration_type in ('semanas', 'horas'):
            try:
                duration_value = int(data.get('duration_value', 0))
                if duration_value <= 0:
                    return jsonify({'error': 'duration_value debe ser mayor que 0'}), 400
            except (TypeError, ValueError):
                return jsonify({'error': 'duration_value debe ser un número'}), 400
        signed = bool(data.get('signed', False))
        signature_data = data.get('signature_data') or data.get('signature')
        if signature_data:
            signed = True
        stock_id = data.get('stock_id')
        if stock_id is not None:
            try:
                stock_id = int(stock_id)
                if Stock.query.get(stock_id) is None:
                    stock_id = None
            except (TypeError, ValueError):
                stock_id = None

        r = ItemRequest(
            user_id=user.id,
            tenant_id=user.tenant_id,
            request_username=user.username,
            stock_id=stock_id,
            request_date=req_date,
            duration_type=duration_type,
            duration_value=duration_value,
            signed=signed,
            signed_at=datetime.utcnow() if signed else None,
            signature_data=signature_data,
        )
        db.session.add(r)
        db.session.commit()
        return jsonify({
            'id': r.id,
            'message': 'Solicitud registrada',
            'request_date': r.request_date.isoformat(),
            'duration_type': r.duration_type,
            'duration_value': r.duration_value,
            'signed': r.signed,
            'stock_id': r.stock_id,
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al crear la solicitud', 'message': str(e)}), 500


@solicitudes.route('/<int:req_id>/sign', methods=['POST'])
@jwt_required()
def sign_solicitud(req_id):
    """Firma digital del solicitante (canvas base64)."""
    user, err = _current_user_or_401()
    if err:
        return jsonify({'error': 'No autorizado'}), err
    r = ItemRequest.query.get(req_id)
    if not r:
        return jsonify({'error': 'Solicitud no encontrada'}), 404
    if r.user_id != user.id and user.user_type.value != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    data = request.get_json() or {}
    sig = data.get('signature_data') or data.get('signature')
    if not sig:
        return jsonify({'error': 'signature_data es obligatorio'}), 400
    r.signature_data = sig
    r.signed = True
    r.signed_at = datetime.utcnow()
    db.session.commit()
    return jsonify(_serialize_solicitud(r)), 200


@solicitudes.route('/<int:req_id>', methods=['PATCH'])
@jwt_required()
@role_required('admin')
def update_solicitud(req_id):
    try:
        r = ItemRequest.query.get(req_id)
        if not r:
            return jsonify({'error': 'Solicitud no encontrada'}), 404
        data = request.get_json() or {}
        if 'status' in data:
            s = (data.get('status') or '').strip().lower()
            if s in ('aprobado', 'rechazado', 'pendiente'):
                r.status = s
        if 'delivery_date' in data:
            v = data['delivery_date']
            if v:
                try:
                    r.delivery_date = datetime.strptime(v, '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    pass
            else:
                r.delivery_date = None
        db.session.commit()
        return jsonify(_serialize_solicitud(r)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
