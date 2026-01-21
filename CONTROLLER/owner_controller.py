from flask import Blueprint, jsonify, session
from SERVICES.owner_service import OwnerService
from UTILS.decorators import role_required

owner_bp = Blueprint('owner_bp', __name__)

@owner_bp.route('/api/owner/dashboard-data', methods=['GET'])
@role_required(2) # Solo dueños
def get_dashboard_data():
    user_id = session.get('user_id')
    try:
        # Supongamos que tu servicio obtiene estadísticas
        stats = OwnerService.get_owner_stats(user_id)
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500