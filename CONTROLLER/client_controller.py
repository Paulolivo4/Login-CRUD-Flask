from flask import Blueprint, jsonify, request, session
from SERVICES.client_service import ClientService
from UTILS.decorators import role_required

client_bp = Blueprint('client_bp', __name__)

@client_bp.route('/client/restaurants', methods=['GET'])
def get_restaurants():
    try:
        restaurants = ClientService.get_all_restaurants()
        
        if not restaurants:
            return jsonify([]), 200

        data = []
        for r in restaurants:
            data.append({
                'id': getattr(r, 'ID_RESTAURANTE', None),
                'name': getattr(r, 'NOMBRE', 'Sin nombre'),
                'address': getattr(r, 'DIRECCION', 'Sin dirección'),
                'phone': getattr(r, 'TELEFONO', 'N/A'),
                'image_url': getattr(r, 'IMAGEN_URL', None)
            })
        return jsonify(data), 200
    except Exception as e:
        print(f"DEBUG Error en get_restaurants: {str(e)}")
        return jsonify({'error': 'Error al cargar restaurantes', 'details': str(e)}), 500

@client_bp.route('/client/restaurant/<int:restaurant_id>/menus', methods=['GET'])
def get_menus(restaurant_id):
    try:
        menus = ClientService.get_menus_by_restaurant(restaurant_id)
        if not menus:
            return jsonify([]), 200

        data = [{
            'id': getattr(m, 'ID_MENU', None),
            'name': getattr(m, 'NOMBRE_PLATO', 'Plato'),
            'description': getattr(m, 'DESCRIPCION', ''),
            'price': float(getattr(m, 'PRECIO', 0)),
            'image_url': getattr(m, 'FOTO_PLATO', None)
        } for m in menus]
        return jsonify(data), 200
    except Exception as e:
        print(f"DEBUG Error en get_menus: {str(e)}")
        return jsonify({'error': 'Error al cargar menú', 'details': str(e)}), 500

@client_bp.route('/client/reserve', methods=['POST'])
@role_required(3) 
def create_reservation():
    data = request.json
    user_id = session.get('user_id')
    
    try:
        ClientService.create_reservation(
            user_id=user_id,
            menu_id=data.get('menu_id'),
            date=data.get('date'),
            people=data.get('people'),
            total=data.get('total')
        )
        return jsonify({'message': 'Reserva creada con éxito'}), 201
    except Exception as e:
        return jsonify({'error': 'No se pudo crear la reserva', 'details': str(e)}), 500