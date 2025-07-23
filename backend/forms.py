from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Form, DetailForm, User, UserTypeEnum

forms = Blueprint('forms', __name__)

@forms.route('', methods=['GET'])
@jwt_required()
def get_forms():
    try:
        forms = Form.query.all()
        return jsonify([form.to_dict() for form in forms]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@forms.route('/<int:form_id>', methods=['GET'])
@jwt_required()
def get_form(form_id):
    try:
        form = Form.query.get(form_id)
        if not form:
            return jsonify({'error': 'Formulario no encontrado'}), 404
        return jsonify(form.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@forms.route('', methods=['POST'])
@jwt_required()
def create_form():
    try:
        data = request.json
        new_form = Form(**data)
        db.session.add(new_form)
        db.session.commit()
        return jsonify(new_form.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@forms.route('/<int:form_id>', methods=['PUT'])
@jwt_required()
def update_form(form_id):
    try:
        form = Form.query.get(form_id)
        if not form:
            return jsonify({'error': 'Formulario no encontrado'}), 404
        
        data = request.json
        for key, value in data.items():
            setattr(form, key, value)
        
        db.session.commit()
        return jsonify(form.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@forms.route('/<int:form_id>', methods=['DELETE'])
@jwt_required()
def delete_form(form_id):
    try:
        form = Form.query.get(form_id)
        if not form:
            return jsonify({'error': 'Formulario no encontrado'}), 404
        
        db.session.delete(form)
        db.session.commit()
        return jsonify({'message': 'Formulario eliminado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Detail Form routes
@forms.route('/<int:form_id>/details', methods=['GET'])
@jwt_required()
def get_form_details(form_id):
    try:
        details = DetailForm.query.filter_by(form_id=form_id).all()
        return jsonify([detail.to_dict() for detail in details]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@forms.route('/<int:form_id>/details', methods=['POST'])
@jwt_required()
def add_form_detail(form_id):
    try:
        data = request.json
        data['form_id'] = form_id
        new_detail = DetailForm(**data)
        db.session.add(new_detail)
        db.session.commit()
        return jsonify(new_detail.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@forms.route('/<int:form_id>/details/<int:detail_id>', methods=['PUT'])
@jwt_required()
def update_form_detail(form_id, detail_id):
    try:
        detail = DetailForm.query.filter_by(id=detail_id, form_id=form_id).first()
        if not detail:
            return jsonify({'error': 'Detalle no encontrado'}), 404
        
        data = request.json
        for key, value in data.items():
            if key != 'form_id':  # Prevent changing form_id
                setattr(detail, key, value)
        
        db.session.commit()
        return jsonify(detail.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@forms.route('/<int:form_id>/details/<int:detail_id>', methods=['DELETE'])
@jwt_required()
def delete_form_detail(form_id, detail_id):
    try:
        detail = DetailForm.query.filter_by(id=detail_id, form_id=form_id).first()
        if not detail:
            return jsonify({'error': 'Detalle no encontrado'}), 404
        
        db.session.delete(detail)
        db.session.commit()
        return jsonify({'message': 'Detalle eliminado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 