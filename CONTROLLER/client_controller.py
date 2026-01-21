from flask import Blueprint, jsonify, request, session
from SERVICES.client_service import ClientService
from UTILS.decorators import role_required

client_bp = Blueprint('client_bp', __name__)

@client_bp.route('/api/client/restaurants', methods=['GET'])
# @role_required(3) # Opcional: si quieres que sea público o solo clientes
def get_restaurants():
    try:
        restaurants = ClientService.get_all_restaurants()
        data = [{
            'id': r.ID_RESTAURANTE,
            'name': r.NOMBRE,
            'address': r.DIRECCION,
            'phone': r.TELEFONO,
            'image_url': r.IMAGEN_URL if hasattr(r, 'IMAGEN_URL') else None
        } for r in restaurants]
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@client_bp.route('/api/client/restaurant/<int:restaurant_id>/menus', methods=['GET'])
def get_menus(restaurant_id):
    try:
        menus = ClientService.get_menus_by_restaurant(restaurant_id)
        data = [{
            'id': m.ID_MENU,
            'name': m.NOMBRE_PLATO,
            'description': m.DESCRIPCION,
            'price': float(m.PRECIO),
            'image_url': m.FOTO_PLATO
        } for m in menus]
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@client_bp.route('/api/client/reserve', methods=['POST'])
@role_required(3) # Solo clientes
def create_reservation():
    data = request.json
    user_id = session.get('user_id')
    
    try:
        # Asegúrate de pasar todos los datos necesarios al servicio
        ClientService.create_reservation(
            user_id=user_id,
            menu_id=data.get('menu_id'),
            date=data.get('date'),
            people=data.get('people'),
            total=data.get('total')
        )
        return jsonify({'message': 'Reserva creada con éxito'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500