from flask import Blueprint, jsonify, session, request
from SERVICES.owner_service import OwnerService
from UTILS.decorators import role_required
import traceback

owner_bp = Blueprint('owner_bp', __name__)

# QUITAMOS el /api porque ya lo pone el app.py globalmente
@owner_bp.route('/owner/dashboard-data', methods=['GET'])
@role_required(2) # Solo dueños
def get_dashboard_data():
    user_id = session.get('user_id')
    print(f"[dashboard-data] Cargando para user_id: {user_id}")
    
    try:
        # Obtener todas las estadísticas del dueño
        stats = OwnerService.get_owner_stats(user_id)
        print(f"[dashboard-data] Stats obtenidas: {stats}")
        
        if 'error' in stats:
            return jsonify(stats), 400
        
        # Obtener el restaurante del dueño
        restaurant = OwnerService.get_owner_restaurant(user_id)
        print(f"[dashboard-data] Restaurante: {restaurant}")
        
        restaurant_id = restaurant[0] if restaurant else None
        
        # Obtener menús del restaurante
        menus_list = OwnerService.get_menus(user_id)
        print(f"[dashboard-data] Menús encontrados: {len(menus_list) if menus_list else 0}")
        
        # Formatear menús para el frontend
        menus_data = []
        if menus_list:
            for m in menus_list:
                try:
                    menu_dict = {
                        'id': m[0] if len(m) > 0 else None,
                        'restaurant_id': m[1] if len(m) > 1 else restaurant_id,
                        'nombre': m[2] if len(m) > 2 else 'Sin nombre',
                        'descripcion': m[3] if len(m) > 3 else '',
                        'precio': float(m[4]) if len(m) > 4 and m[4] else 0.0,
                        'disponible': m[5] if len(m) > 5 else True,
                        'foto': m[6] if len(m) > 6 else None
                    }
                    menus_data.append(menu_dict)
                except Exception as menu_error:
                    print(f"[dashboard-data] Error procesando menú: {menu_error}")
                    continue
        
        # Obtener reservas del restaurante
        reservations_data = []
        
        try:
            from MODEL.models import Reserva, LoginDetails
            from BDD.db import db
            
            print(f"[dashboard-data] Buscando reservas para restaurante_id: {restaurant_id}")
            
            if restaurant_id:
                # Query para obtener reservas con info del cliente
                reservations = db.session.query(
                    Reserva.ID_RESERVA,
                    LoginDetails.NAME.label('cliente_nombre'),
                    Reserva.FECHA_RESERVA,
                    Reserva.CANTIDAD_PERSONAS,
                    Reserva.ESTADO
                ).join(
                    LoginDetails, Reserva.ID_CLIENTE == LoginDetails.ID
                ).filter(
                    Reserva.ID_RESTAURANTE == restaurant_id
                ).all()
                
                print(f"[dashboard-data] Reservas encontradas: {len(reservations)}")
                
                for res in reservations:
                    try:
                        reservations_data.append({
                            'id': res.ID_RESERVA,
                            'cliente': res.cliente_nombre or 'Cliente anónimo',
                            'fecha': str(res.FECHA_RESERVA) if res.FECHA_RESERVA else 'N/A',
                            'personas': res.CANTIDAD_PERSONAS,
                            'plato': 'Plato reservado',
                            'metodo_pago': 'TARJETA',
                            'estado_pago': 'PAGADO',
                            'total': 0.00
                        })
                    except Exception as res_error:
                        print(f"[dashboard-data] Error procesando reserva: {res_error}")
                        continue
            else:
                print("[dashboard-data] No existe restaurante para este dueño")
                
        except Exception as e:
            print(f"[dashboard-data] Error obteniendo reservas: {e}")
            traceback.print_exc()
        
        # Retornar estructura esperada por el frontend
        response_data = {
            'restaurant': {
                'id': restaurant_id,
                'nombre': restaurant[1] if restaurant and len(restaurant) > 1 else 'Sin nombre',
                'owner_id': restaurant[2] if restaurant and len(restaurant) > 2 else user_id
            },
            'menus': menus_data,
            'reservations': reservations_data,
            'stats': stats
        }
        
        print(f"[dashboard-data] Respuesta lista: {len(menus_data)} menús, {len(reservations_data)} reservas")
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"[dashboard-data] ERROR general: {e}")
        traceback.print_exc()
        return jsonify({
            'error': 'Error cargando datos del dashboard',
            'details': str(e)
        }), 500
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