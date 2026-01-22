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
        # 1. Estadísticas Generales
        stats = OwnerService.get_owner_stats(user_id)
        if 'error' in stats: return jsonify(stats), 400
        
        # 2. Información del Restaurante
        restaurant = OwnerService.get_owner_restaurant(user_id)
        restaurant_id = restaurant[0] if restaurant else None
        
        # 3. Lista de Menús
        menus_list = OwnerService.get_menus(user_id)
        menus_data = []
        
        # Calculamos un precio promedio para usar en las reservas si falta info
        precio_promedio = 15.00 
        if menus_list:
            total_precios = sum([float(m[4]) for m in menus_list if m[4]])
            if len(menus_list) > 0:
                precio_promedio = total_precios / len(menus_list)

            for m in menus_list:
                # Solo mostramos en la lista los que están DISPONIBLES (True)
                # m[5] es la columna DISPONIBLE
                if m[5]: 
                    menus_data.append({
                        'id': m[0],
                        'restaurant_id': m[1],
                        'nombre': m[2],
                        'descripcion': m[3],
                        'precio': float(m[4]),
                        'disponible': m[5],
                        'foto': m[6]
                    })
        
        # 4. Lista de Reservas (Con Cálculo de Total)
        reservations_data = []
        if restaurant_id:
            from MODEL.models import Reserva, LoginDetails
            from BDD.db import db
            
            reservations = db.session.query(
                Reserva.ID_RESERVA,
                LoginDetails.NAME.label('cliente_nombre'),
                LoginDetails.LASTNAME.label('cliente_apellido'),
                Reserva.FECHA_RESERVA,
                Reserva.CANTIDAD_PERSONAS,
                Reserva.ESTADO
            ).join(
                LoginDetails, Reserva.ID_CLIENTE == LoginDetails.ID
            ).filter(
                Reserva.ID_RESTAURANTE == restaurant_id
            ).all()
            
            for res in reservations:
                # CÁLCULO DEL TOTAL:
                # Como la tabla Reserva no tiene el precio guardado, usamos el promedio
                # o un precio fijo estimado para que no salga $0.
                personas = res.CANTIDAD_PERSONAS if res.CANTIDAD_PERSONAS else 1
                total_estimado = personas * precio_promedio
                
                reservations_data.append({
                    'id': res.ID_RESERVA,
                    'cliente': f"{res.cliente_nombre} {res.cliente_apellido}",
                    'fecha': str(res.FECHA_RESERVA),
                    'personas': personas,
                    'plato': 'Reserva General', # Tu modelo no guarda el plato específico
                    'metodo_pago': 'Tarjeta',
                    'estado_pago': 'PAGADO',
                    'total': round(total_estimado, 2) # <--- AQUÍ ESTÁ EL ARREGLO
                })

        response_data = {
            'restaurant': {
                'id': restaurant_id,
                'nombre': restaurant[1] if restaurant else 'Sin nombre',
            },
            'menus': menus_data,
            'reservations': reservations_data,
            'stats': stats
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"[dashboard-data] ERROR: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Error cargando datos', 'details': str(e)}), 500
    
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