from flask import Blueprint, jsonify, session, request
from SERVICES.user_service import UserService
from SERVICES.authentication_service import AuthenticationService
import traceback

user_bp = Blueprint('user_bp', __name__)

# --- MIDDLEWARE DE SEGURIDAD ---
def check_admin():
    role = session.get('user_role')
    if not AuthenticationService.is_admin(role):
        return False
    return True

# =================================================================
# 1. ENDPOINT DE ESTADÍSTICAS (PARA LOS GRÁFICOS)
# =================================================================
@user_bp.route('/users/stats', methods=['GET'])
def get_stats():
    if not check_admin(): return jsonify({'error': 'No autorizado'}), 403

    try:
        users = UserService.get_all_users()
        
        # Simularemos datos de "Sesiones Activas" y "Reservas" calculándolos
        # En un sistema real, harías count() directos a la BD.
        
        stats = {
            'total_users': len(users),
            'active_sessions': 0, # Calcularemos abajo
            'roles_distribution': {'Admin': 0, 'Dueño': 0, 'Cliente': 0},
            'reservations_by_user': [] # Top 5 usuarios con más actividad
        }

        # Procesamos datos para los gráficos
        for u in users:
            # Tupla vs Diccionario (Normalización)
            role_id = u.get('ROL_ID') if isinstance(u, dict) else (u[5] if len(u)>5 else 3)
            
            # Contar roles para el gráfico de pastel
            if role_id == 1: stats['roles_distribution']['Admin'] += 1
            elif role_id == 2: stats['roles_distribution']['Dueño'] += 1
            else: stats['roles_distribution']['Cliente'] += 1

            # Simulación: Asumimos que 1 de cada 5 usuarios está "logueado" ahora mismo
            # (Para hacerlo real necesitaríamos una tabla de sesiones activas en BD)
            import random
            if random.choice([True, False, False, False, False]): 
                stats['active_sessions'] += 1

        return jsonify(stats), 200

    except Exception as e:
        print(f"Error stats: {e}")
        return jsonify({'error': 'Error cargando estadísticas'}), 500

# =================================================================
# 2. CRUD: LEER USUARIOS (Ya lo tenías, ajustado)
# =================================================================
@user_bp.route('/users/dashboard', methods=['GET'])
def list_users():
    if not check_admin(): return jsonify({'error': 'No autorizado'}), 403

    try:
        users = UserService.get_all_users()
        users_list = []
        for u in users:
            # Normalización segura de datos
            if isinstance(u, dict):
                u_data = {'id': u.get('ID'), 'name': u.get('NAME'), 'lastname': u.get('LASTNAME'), 'email': u.get('EMAIL'), 'role_id': u.get('ROL_ID')}
            else:
                u_data = {'id': u[0], 'name': u[1], 'lastname': u[2], 'email': u[3], 'role_id': u[5] if len(u)>5 else 3}
            users_list.append(u_data)
            
        return jsonify(users_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =================================================================
# 3. CRUD: CREAR USUARIO
# =================================================================
@user_bp.route('/users/create', methods=['POST'])
def create_user():
    if not check_admin(): return jsonify({'error': 'No autorizado'}), 403
    
    data = request.get_json()
    try:
        # Llamamos al servicio (asegúrate que UserService tenga create_user)
        UserService.create_user(
            data.get('name'), data.get('lastname'), 
            data.get('email'), data.get('password'), data.get('role_id')
        )
        return jsonify({'message': 'Usuario creado correctamente'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# =================================================================
# 4. CRUD: EDITAR USUARIO
# =================================================================
@user_bp.route('/users/update/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    if not check_admin(): return jsonify({'error': 'No autorizado'}), 403
    
    data = request.get_json()
    try:
        # Llamamos al nuevo método real que acabamos de crear
        UserService.update_user_details(
            user_id,
            data.get('name'), 
            data.get('lastname'), 
            data.get('email'), 
            data.get('role_id')
        )
        return jsonify({'message': 'Usuario y Rol actualizados correctamente'}), 200
    except Exception as e:
        print(f"Error update: {e}")
        return jsonify({'error': str(e)}), 400
# =================================================================
# 5. CRUD: ELIMINAR USUARIO
# =================================================================
@user_bp.route('/users/delete/<email>', methods=['DELETE'])
def delete_user(email):
    if not check_admin(): return jsonify({'error': 'No autorizado'}), 403

    try:
        UserService.delete_user(email)
        return jsonify({'message': 'Usuario eliminado'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    

# =================================================================
@user_bp.route('/users/available-owners', methods=['GET'])
def get_available_owners():
    try:
        # Verificar admin
        role = session.get('user_role')
        if not AuthenticationService.is_admin(role):
            return jsonify({'error': 'No autorizado'}), 403
        
        print("[available-owners] Iniciando búsqueda...")
        
        # Obtener dueños sin restaurante directamente de la BD
        from BDD.db import db
        from sqlalchemy import text
        
        sql = text("""
            SELECT U.ID, U.NOMBRE, U.APELLIDO, U.EMAIL 
            FROM LOGINDETAILS U
            LEFT JOIN RESTAURANTE R ON U.ID = R.ID_DUENO
            WHERE U.ROL_ID = 2 AND R.ID_DUENO IS NULL
        """)
        
        result = db.session.execute(sql)
        owners = result.fetchall()
        print(f"[available-owners] {len(owners)} dueños encontrados")
        
        owners_list = []
        for row in owners:
            try:
                # Acceder directamente por índice (es más confiable)
                owner_dict = {
                    'id': row[0],
                    'name': f"{row[1]} {row[2]}",
                    'email': row[3]
                }
                owners_list.append(owner_dict)
                print(f"[available-owners] Owner procesado: {owner_dict}")
            except Exception as e:
                print(f"[available-owners] Error en fila: {e}, fila={row}")
                continue
        
        return jsonify(owners_list), 200
        
    except Exception as e:
        print(f"[available-owners] ERROR: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': 'Error cargando dueños disponibles', 'details': str(e)}), 500