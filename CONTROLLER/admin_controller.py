from flask import Blueprint, jsonify, request
from SERVICES.admin_service import AdminService
from UTILS.decorators import role_required

admin_bp = Blueprint('admin_bp', __name__)

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