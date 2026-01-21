from flask import Blueprint, jsonify, request
from SERVICES.admin_service import AdminService
from UTILS.decorators import role_required
from repositories.azure_user_repository import AzureUserRepository
import logging

admin_bp = Blueprint('admin_bp', __name__)
logger = logging.getLogger(__name__)

# ==========================================
# RUTAS DE ADMINISTRACIÓN (Limpio de /api)
# ==========================================

@admin_bp.route('/admin/users', methods=['GET']) # ELIMINADO EL /api INICIAL
@role_required(1)
def get_all_users():
    try:
        users = AdminService.get_all_users()
        users_list = [{
            'id': u.ID if hasattr(u, 'ID') else u.get('ID'),
            'name': u.NAME if hasattr(u, 'NAME') else u.get('NAME'),
            'lastname': u.LASTNAME if hasattr(u, 'LASTNAME') else u.get('LASTNAME'),
            'email': u.EMAIL if hasattr(u, 'EMAIL') else u.get('EMAIL'),
            'role_id': u.ROL_ID if hasattr(u, 'ROL_ID') else u.get('ROL_ID')
        } for u in users]
        return jsonify(users_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/user/<int:user_id>', methods=['DELETE']) 
@role_required(1)
def delete_user(user_id):
    try:
        if AdminService.delete_user(user_id):
            return jsonify({'message': 'Usuario eliminado'}), 200
        return jsonify({'error': 'Usuario no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/admin/user/<int:user_id>', methods=['PUT']) 
@role_required(1)
def update_user(user_id):
    data = request.json
    try:
        success = AdminService.update_user(user_id, data)
        if success:
            return jsonify({'message': 'Usuario actualizado'}), 200
        return jsonify({'error': 'No se pudo actualizar'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500      
    
@admin_bp.route('/admin/dashboard-data', methods=['GET'])
def dashboard_data_api():
    try:
        user_repo = AzureUserRepository()
        all_users = user_repo.get_all_users()
        all_restaurants = AdminService.get_all_restaurants()

        # Manejar tanto objetos como diccionarios
        def get_role_id(u):
            if isinstance(u, dict):
                return u.get('ROL_ID')
            return getattr(u, 'ROL_ID', None)
        
        admins = len([u for u in all_users if get_role_id(u) == 1])
        owners = len([u for u in all_users if get_role_id(u) == 2])
        clients = len([u for u in all_users if get_role_id(u) == 3])
        
        data = {
            'users_distribution': {
                'labels': ['Administradores', 'Dueños', 'Clientes'],
                'data': [admins, owners, clients]
            },
            'total_restaurants': len(all_restaurants),
            'recent_activity': []
        }
        return jsonify(data), 200
    except Exception as e:
        print(f"Error obteniendo datos del dashboard: {e}")
        return jsonify({'error': 'Error interno', 'details': str(e)}), 500