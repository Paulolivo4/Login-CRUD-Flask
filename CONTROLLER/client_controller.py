from flask import Blueprint, jsonify, request, session
from SERVICES.client_service import ClientService
from UTILS.decorators import role_required

client_bp = Blueprint('client_bp', __name__)

# QUITAMOS el /api porque ya lo pone el app.py
@client_bp.route('/client/restaurants', methods=['GET'])
def get_restaurants():
    try:
        restaurants = ClientService.get_all_restaurants()
        if not restaurants:
            return jsonify([]), 200
            
        data = []
        for r in restaurants:
            try:
                resto_data = {
                    'id': getattr(r, 'ID_RESTAURANTE', None),
                    'nombre': getattr(r, 'NOMBRE', 'Sin nombre'),
                    'direccion': getattr(r, 'DIRECCION', 'Sin dirección'),
                    'foto': getattr(r, 'RUTAFOTOLOGO', None),
                    'horario': '09:00 - 22:00'
                }
                data.append(resto_data)
            except Exception as item_error:
                print(f"Error procesando restaurante: {item_error}")
                continue
        
        return jsonify(data), 200
    except Exception as e:
        print(f"Error en get_restaurants: {e}")
        return jsonify({'error': str(e), 'type': type(e).__name__}), 500
        
@client_bp.route('/client/restaurant/<int:restaurant_id>/menus', methods=['GET'])
def get_menus(restaurant_id):
    try:
        print(f"[DEBUG] Pidiendo menús para restaurante {restaurant_id}")
        menus = ClientService.get_menus_by_restaurant(restaurant_id)
        print(f"[DEBUG] Encontrados {len(menus)} menús")
        
        if not menus:
            print(f"[DEBUG] No hay menús disponibles para restaurante {restaurant_id}")
            return jsonify([]), 200

        data = []
        for m in menus:
            try:
                menu_data = {
                    'id': getattr(m, 'ID_MENU', None),
                    'nombre': getattr(m, 'NOMBRE_PLATO', 'Plato'),
                    'descripcion': getattr(m, 'DESCRIPCION', ''),
                    'precio': float(getattr(m, 'PRECIO', 0)),
                    'foto': getattr(m, 'RUTAFOTOMENU', None)
                }
                print(f"[DEBUG] Menú: {menu_data}")
                data.append(menu_data)
            except Exception as menu_error:
                print(f"[ERROR] Procesando menú: {menu_error}")
                continue
        
        return jsonify(data), 200
    except Exception as e:
        print(f"[ERROR] get_menus: {e}")
        import traceback
        traceback.print_exc()
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
        return jsonify({'error': 'No pudo crearse', 'details': str(e)}), 500