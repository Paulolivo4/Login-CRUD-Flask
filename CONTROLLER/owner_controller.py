from flask import Blueprint, jsonify, session
from SERVICES.owner_service import OwnerService
from UTILS.decorators import role_required

owner_bp = Blueprint('owner_bp', __name__)

# QUITAMOS el /api porque ya lo pone el app.py globalmente
@owner_bp.route('/owner/dashboard-data', methods=['GET'])
@role_required(2) # Solo dueños
def get_dashboard_data():
    user_id = session.get('user_id')
    try:
        # El servicio obtendrá las estadísticas del dueño actual
        stats = OwnerService.get_owner_stats(user_id)
        return jsonify(stats), 200
    except Exception as e:
        print(f"DEBUG Error en owner dashboard: {e}")
        return jsonify({'error': 'Error al cargar estadísticas del dueño', 'details': str(e)}), 500