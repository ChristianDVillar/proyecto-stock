"""
Error handlers
Centralized error handling
"""
from flask import jsonify, g


def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            'error': 'Recurso no encontrado',
            'message': 'La ruta solicitada no existe'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        if hasattr(g, 'session'):
            g.session.rollback()
        return jsonify({
            'error': 'Error interno del servidor',
            'message': 'Ocurrió un error inesperado'
        }), 500
    
    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({
            'error': 'Solicitud inválida',
            'message': str(error.description) if hasattr(error, 'description') else 'Datos inválidos'
        }), 400
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return jsonify({
            'error': 'Acceso prohibido',
            'message': 'No tienes permisos para realizar esta acción'
        }), 403
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        if hasattr(g, 'session'):
            g.session.rollback()
        
        # Log error (in production, use proper logging)
        import traceback
        print(f"Unhandled exception: {str(e)}")
        print(traceback.format_exc())
        
        return jsonify({
            'error': 'Error del servidor',
            'message': 'Ocurrió un error inesperado',
            'type': str(type(e).__name__)
        }), 500
