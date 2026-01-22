from flask import Blueprint, jsonify, session, request
from SERVICES.owner_service import OwnerService
from UTILS.decorators import role_required

owner_bp = Blueprint('owner_bp', __name__)

# QUITAMOS el /api porque ya lo pone el app.py globalmente
@owner_bp.route('/owner/dashboard-data', methods=['GET'])
@role_required(2) # Solo dueños
def get_dashboard_data():
    user_id = session.get('user_id')
    try:
        # Obtener todas las estadísticas del dueño
        stats = OwnerService.get_owner_stats(user_id)
        
        if 'error' in stats:
            return jsonify(stats), 400
        
        # Obtener el restaurante del dueño
        restaurant = OwnerService.get_owner_restaurant(user_id)
        restaurant_id = restaurant[0] if restaurant else None
        
        # Obtener menús del restaurante
        menus_list = OwnerService.get_menus(user_id)
        
        # Formatear menús para el frontend
        menus_data = []
        for m in menus_list:
            menu_dict = {
                'id': m[0],  # ID_MENU
                'restaurant_id': m[1],  # ID_RESTAURANTE
                'nombre': m[2],  # NOMBRE_PLATO
                'descripcion': m[3],  # DESCRIPCION
                'precio': m[4],  # PRECIO
                'disponible': m[5],  # DISPONIBLE
                'foto': m[6]  # RUTAFOTOMENU
            }
            menus_data.append(menu_dict)
        
        # TODO: Obtener reservas del restaurante (si existe tabla de reservas con info de cliente)
        # Por ahora, retornar lista vacía
        reservations_data = []
        
        # Intentar obtener reservas si existen
        try:
            from MODEL.models import Reserva, LoginDetails
            from BDD.db import db
            
            # Query para obtener reservas con info del cliente
            reservations = db.session.query(
                Reserva.ID_RESERVA,
                LoginDetails.NOMBRE.label('cliente_nombre'),
                Reserva.FECHA_RESERVA,
                Reserva.CANTIDAD_PERSONAS,
                Reserva.ESTADO
            ).join(
                LoginDetails, Reserva.ID_CLIENTE == LoginDetails.ID
            ).filter(
                Reserva.ID_RESTAURANTE == restaurant_id
            ).all()
            
            for res in reservations:
                reservations_data.append({
                    'id': res.ID_RESERVA,
                    'cliente': res.cliente_nombre or 'Cliente anónimo',
                    'fecha': str(res.FECHA_RESERVA) if res.FECHA_RESERVA else 'N/A',
                    'personas': res.CANTIDAD_PERSONAS,
                    'plato': 'Plato reservado',  # TODO: obtener del menú si está disponible
                    'metodo_pago': 'TARJETA',  # TODO: guardar en tabla RESERVA
                    'estado_pago': 'PAGADO',  # TODO: determinar si está pagado
                    'total': 0.00  # TODO: guardar en tabla RESERVA
                })
        except Exception as e:
            print(f"Error obteniendo reservas: {e}")
        
        # Retornar estructura esperada por el frontend
        response_data = {
            'restaurant': {
                'id': restaurant_id,
                'nombre': restaurant[1] if restaurant else 'Sin nombre',
                'owner_id': restaurant[2] if restaurant else user_id
            },
            'menus': menus_data,
            'reservations': reservations_data,
            'stats': stats
        }
        
        return jsonify(response_data), 200
    except Exception as e:
        print(f"DEBUG Error en owner dashboard: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Error al cargar estadísticas del dueño', 'details': str(e)}), 500

@owner_bp.route('/owner/menu/create', methods=['POST'])
@role_required(2)
def create_menu():
    user_id = session.get('user_id')
    try:
        # Soportar tanto JSON como FormData
        if request.is_json:
            data = request.json
        else:
            data = request.form
        
        # Obtener el restaurante del dueño
        restaurant = OwnerService.get_owner_restaurant(user_id)
        if not restaurant:
            return jsonify({'error': 'No restaurante encontrado para este dueño'}), 400
        
        restaurant_id = restaurant[0]
        
        # Obtener la foto si viene en files
        photo_url = None
        if 'foto' in request.files:
            # TODO: implementar subida de archivos a cloud storage
            pass
        
        # Crear el menú
        OwnerService.create_menu(
            restaurant_id=restaurant_id,
            dish_name=data.get('nombre'),
            description=data.get('descripcion'),
            price=float(data.get('precio', 0)),
            photo_url=photo_url
        )
        
        return jsonify({'message': 'Plato creado correctamente'}), 201
    except Exception as e:
        print(f"Error creando menú: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Error al crear plato', 'details': str(e)}), 500

@owner_bp.route('/owner/menu/delete/<int:menu_id>', methods=['DELETE'])
@role_required(2)
def delete_menu(menu_id):
    try:
        OwnerService.delete_menu(menu_id)
        return jsonify({'message': 'Plato eliminado correctamente'}), 200
    except Exception as e:
        print(f"Error eliminando menú: {e}")
        return jsonify({'error': 'Error al eliminar plato', 'details': str(e)}), 500