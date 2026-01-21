from flask import Blueprint, jsonify, request
from SERVICES.admin_service import AdminService
from UTILS.decorators import role_required
from repositories.azure_user_repository import AzureUserRepository
import logging
admin_bp = Blueprint('admin_bp', __name__)
logger = logging.getLogger(__name__)
# Solo API - Devuelve JSON
@admin_bp.route('/api/admin/users', methods=['GET'])
@role_required(1)  # 1 = Admin
def get_all_users():
    try:
        users = AdminService.get_all_users()
        # Convertimos objetos a lista de diccionarios
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

@admin_bp.route('/api/admin/user/<int:user_id>', methods=['DELETE'])
@role_required(1)
def delete_user(user_id):
    try:
        if AdminService.delete_user(user_id):
            return jsonify({'message': 'Usuario eliminado'}), 200
        return jsonify({'error': 'Usuario no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/user/<int:user_id>', methods=['PUT'])
@role_required(1)
def update_user(user_id):
    data = request.json
    try:
        # Asumiendo que tu servicio tiene un método update
        success = AdminService.update_user(user_id, data)
        if success:
            return jsonify({'message': 'Usuario actualizado'}), 200
        return jsonify({'error': 'No se pudo actualizar'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500      
    
@admin_bp.route('/dashboard-data', methods=['GET'])
def dashboard_data_api():
    """
    Endpoint para alimentar los gráficos del Dashboard de Admin.
    """
    try:
        # Instanciamos los repositorios necesarios
        user_repo = AzureUserRepository()
        # AdminService ya lo tienes importado
        
        # 1. Obtener conteos reales
        # Si no tienes métodos específicos de 'count', traemos todos y usamos len()
        # (Para apps pequeñas esto está bien, para grandes es mejor hacer COUNT en SQL)
        all_users = user_repo.get_all_users()
        all_restaurants = AdminService.get_all_restaurants()

        # Filtramos por roles (1:Admin, 2:Owner, 3:Client)
        admins = len([u for u in all_users if u.ID_ROL == 1])
        owners = len([u for u in all_users if u.ID_ROL == 2])
        clients = len([u for u in all_users if u.ID_ROL == 3])
        
        restaurants_count = len(all_restaurants)

        # 2. Estructura de datos para los gráficos (Chart.js / Vue)
        data = {
            'users_distribution': {
                'labels': ['Administradores', 'Dueños', 'Clientes'],
                'data': [admins, owners, clients]
            },
            'total_restaurants': restaurants_count,
            'recent_activity': [] # Puedes dejarlo vacío o implementar logs luego
        }
        
        return jsonify(data), 200
    except Exception as e:
        logger.error(f"Error obteniendo datos del dashboard: {e}")
        return jsonify({'error': 'Error interno', 'details': str(e)}), 500