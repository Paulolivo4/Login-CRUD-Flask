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
            'id': u.ID_USUARIO,
            'name': u.NOMBRE,
            'lastname': u.APELLIDO,
            'email': u.CORREO,
            'role_id': u.ID_ROL
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
    
@admin_bp.route('/admin/dashboard-data', methods=['GET']) # ELIMINADO EL /api INICIAL
def dashboard_data_api():
    try:
        user_repo = AzureUserRepository()
        all_users = user_repo.get_all_users()
        all_restaurants = AdminService.get_all_restaurants()

        admins = len([u for u in all_users if u.ID_ROL == 1])
        owners = len([u for u in all_users if u.ID_ROL == 2])
        clients = len([u for u in all_users if u.ID_ROL == 3])
        
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