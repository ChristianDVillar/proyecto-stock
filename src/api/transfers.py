"""Transferencias entre almacenes."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import db
from .utils import role_required
from .services.transfer_service import TransferService

transfers = Blueprint('transfers', __name__)


@transfers.route('', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_transfers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    return jsonify(TransferService.list_transfers(page=page, per_page=per_page)), 200


@transfers.route('', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_transfer():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    transfer, err = TransferService.create_transfer(
        stock_id=data.get('stock_id'),
        from_wh_id=data.get('from_warehouse_id'),
        to_wh_id=data.get('to_warehouse_id'),
        quantity=int(data.get('quantity', 0)),
        user_id=user_id,
        notes=data.get('notes'),
    )
    if err:
        return jsonify({'error': err['error']}), err.get('status', 400)
    db.session.commit()
    return jsonify(transfer.to_dict()), 201


@transfers.route('/<int:transfer_id>/complete', methods=['POST'])
@jwt_required()
@role_required('admin')
def complete_transfer(transfer_id):
    user_id = int(get_jwt_identity())
    transfer, err = TransferService.complete_transfer(transfer_id, user_id)
    if err:
        return jsonify({'error': err['error']}), err.get('status', 400)
    db.session.commit()
    return jsonify(transfer.to_dict()), 200
