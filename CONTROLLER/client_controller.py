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
        print(f"[DEBUG] Datos recibidos: {data}")
        print(f"[DEBUG] User ID: {user_id}")
        
        # Validar datos esenciales
        if not user_id:
            return jsonify({'error': 'Usuario no autenticado'}), 401
        
        restaurant_id = data.get('restaurant_id')
        date_str = data.get('date')
        people = data.get('people')
        
        if not all([restaurant_id, date_str, people]):
            return jsonify({'error': 'Faltan parámetros obligatorios'}), 400
        
        # Convertir la fecha (viene en formato ISO: "2024-01-21T19:30")
        from datetime import datetime
        try:
            reservation_date = datetime.fromisoformat(date_str)
        except ValueError:
            return jsonify({'error': 'Formato de fecha inválido'}), 400
        
        # Crear la reserva
        ClientService.create_reservation(
            client_id=user_id,
            restaurant_id=int(restaurant_id),
            reservation_date=reservation_date,
            number_of_people=int(people)
        )
        
        return jsonify({'message': 'Reserva creada con éxito'}), 201
    except ValueError as ve:
        print(f"[ERROR] Validación: {ve}")
        return jsonify({'error': 'Datos inválidos', 'details': str(ve)}), 400
    except Exception as e:
        print(f"[ERROR] create_reservation: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'No pudo crearse la reserva', 'details': str(e)}), 500