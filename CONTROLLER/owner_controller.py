from flask import Blueprint, jsonify, request, session
from repositories.owner_repository import OwnerRepository
import os
import boto3
import uuid
from botocore.config import Config as BConfig

# Definimos el Blueprint (asegúrate de registrarlo así en app.py)
owner_bp = Blueprint('owner_bp', __name__, url_prefix='/api/owner')
repo = OwnerRepository()

# --- CONFIGURACIÓN S3 ---
S3_BUCKET = os.environ.get('SUPABASE_S3_BUCKET', 'restaurantes') 
S3_ENDPOINT = os.environ.get('SUPABASE_S3_ENDPOINT', 'https://bljzxhufvyectslxmzrr.storage.supabase.co')
SUPABASE_PROJECT = os.environ.get('SUPABASE_PROJECT_REF', 'bljzxhufvyectslxmzrr')
AWS_ACCESS_KEY_ID = os.environ.get('SUPABASE_S3_KEY')
AWS_SECRET_ACCESS_KEY = os.environ.get('SUPABASE_S3_SECRET')

s3_client = boto3.client(
    's3', endpoint_url=S3_ENDPOINT,
    aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    config=BConfig(signature_version='s3v4')
)

# --- MIDDLEWARE DE SEGURIDAD ---
def check_owner():
    role = session.get('user_role')
    # Rol 2 = Dueño
    if not role or int(role) != 2:
        return False
    return True

# --- ENDPOINTS ---

@owner_bp.route('/dashboard-data', methods=['GET'])
def get_dashboard_data():
    if not check_owner(): return jsonify({'error': 'No autorizado'}), 403
    
    owner_id = session.get('user_id')
    
    # Obtener el restaurante del dueño
    restaurant = repo.get_restaurant_by_owner(owner_id)
    
    if not restaurant:
        # Si no tiene restaurante, devolvemos null pero sin error 404 para que el front lo maneje
        return jsonify({
            'restaurant': None,
            'menus': [],
            'reservations': [],
            'stats': {'dishes_count': 0, 'reservations_count': 0, 'total_sales': 0}
        }), 200

    # Cargar datos del restaurante
    menus = repo.get_menus(restaurant['id'])
    reservations = repo.get_reservations_with_details(restaurant['id'])
    
    # Calcular ventas (solo pagadas)
    total_sales = sum(r['total'] for r in reservations if r['estado_pago'] == 'PAGADO')
    
    return jsonify({
        'restaurant': restaurant,
        'menus': menus,
        'reservations': reservations,
        'stats': {
            'dishes_count': len(menus),
            'reservations_count': len(reservations),
            'total_sales': total_sales
        }
    }), 200

@owner_bp.route('/menu/create', methods=['POST'])
def create_menu():
    if not check_owner(): return jsonify({'error': 'No autorizado'}), 403
    
    owner_id = session.get('user_id')
    restaurant = repo.get_restaurant_by_owner(owner_id)
    
    if not restaurant: return jsonify({'error': 'No tienes un restaurante registrado'}), 400

    # Datos del formulario
    nombre = request.form.get('nombre')
    desc = request.form.get('descripcion')
    precio = request.form.get('precio')
    foto_file = request.files.get('foto')
    foto_url = None

    # Subir foto si existe
    if foto_file:
        try:
            ext = foto_file.filename.rsplit('.', 1)[-1] if '.' in foto_file.filename else 'jpg'
            # Nombre único: menus/IDRESTAURANTE_UUID.jpg
            key = f"menus/{restaurant['id']}_{uuid.uuid4().hex}.{ext}"
            
            s3_client.upload_fileobj(
                foto_file, 
                S3_BUCKET, 
                key, 
                ExtraArgs={'ContentType': foto_file.content_type}
            )
            foto_url = f"https://{SUPABASE_PROJECT}.supabase.co/storage/v1/object/public/{S3_BUCKET}/{key}"
        except Exception as e:
            print(f"Error subiendo foto menu: {e}")

    try:
        repo.create_menu(restaurant['id'], nombre, desc, precio, foto_url)
        return jsonify({'message': 'Plato creado exitosamente'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@owner_bp.route('/menu/delete/<int:menu_id>', methods=['DELETE'])
def delete_menu(menu_id):
    if not check_owner(): return jsonify({'error': 'No autorizado'}), 403
    try:
        repo.delete_menu(menu_id)
        return jsonify({'message': 'Plato eliminado'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500