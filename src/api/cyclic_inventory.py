"""Inventarios cíclicos."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import db
from .utils import role_required
from .tenant_utils import get_current_tenant_id
from .services.cyclic_inventory_service import CyclicInventoryService

cyclic_inventory = Blueprint('cyclic_inventory', __name__)


@cyclic_inventory.route('/schedules', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_schedules():
    return jsonify({'schedules': CyclicInventoryService.list_schedules()}), 200


@cyclic_inventory.route('/schedules', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_schedule():
    tid = get_current_tenant_id()
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'error': 'name es obligatorio'}), 400
    sched, err = CyclicInventoryService.create_schedule(
        tenant_id=tid,
        name=name,
        weekday=int(data.get('weekday', 0)),
        device_type=data.get('device_type'),
        warehouse_id=data.get('warehouse_id'),
    )
    if err:
        return jsonify({'error': err['error']}), err.get('status', 400)
    db.session.commit()
    return jsonify(sched.to_dict()), 201


@cyclic_inventory.route('/tasks', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_tasks():
    status = request.args.get('status')
    return jsonify({'tasks': CyclicInventoryService.list_tasks(status=status)}), 200


@cyclic_inventory.route('/tasks/generate', methods=['POST'])
@jwt_required()
@role_required('admin')
def generate_tasks():
    created = CyclicInventoryService.generate_tasks_for_today()
    db.session.commit()
    return jsonify({'created': len(created), 'tasks': [t.to_dict() for t in created]}), 201


@cyclic_inventory.route('/tasks/<int:task_id>/complete', methods=['POST'])
@jwt_required()
@role_required('admin')
def complete_task(task_id):
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    task, err = CyclicInventoryService.complete_task(task_id, user_id, data.get('notes'))
    if err:
        return jsonify({'error': err['error']}), err.get('status', 404)
    db.session.commit()
    return jsonify(task.to_dict()), 200
