from flask import Blueprint, jsonify, session, request
from SERVICES.owner_service import OwnerService
from UTILS.decorators import role_required
import os
import boto3
from botocore.config import Config as BConfig
import uuid
import logging
import traceback

owner_bp = Blueprint('owner_bp', __name__)
logger = logging.getLogger(__name__)

# --- CONFIGURACIÓN SUPABASE (S3) ---
S3_BUCKET = os.environ.get('SUPABASE_S3_BUCKET', 'restaurantes')
S3_ENDPOINT = os.environ.get('SUPABASE_S3_ENDPOINT', 'https://bljzxhufvyectslxmzrr.storage.supabase.co')
SUPABASE_PROJECT = os.environ.get('SUPABASE_PROJECT_REF', 'bljzxhufvyectslxmzrr')
S3_REGION = os.environ.get('SUPABASE_S3_REGION', 'us-east-1')
AWS_ACCESS_KEY_ID = os.environ.get('SUPABASE_S3_KEY')
AWS_SECRET_ACCESS_KEY = os.environ.get('SUPABASE_S3_SECRET')

s3_client = None
if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=S3_ENDPOINT,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=S3_REGION,
            config=BConfig(signature_version='s3v4'),
        )
    except Exception as e:
        logger.error(f"Error S3: {e}")

# --- RUTAS ---

@owner_bp.route('/owner/dashboard-data', methods=['GET'])
@role_required(2)
def get_dashboard_data():
    # ... (Mantén tu lógica de dashboard actual aquí, no la cambies) ...
    # Si quieres puedo pasarte el código del dashboard también, pero si ya te funciona, déjalo.
    pass 
    # NOTA: Como me pediste arreglar la CREACIÓN, me enfocaré en la ruta de abajo.
    # Asegúrate de no borrar tu función get_dashboard_data que ya funcionaba.

@owner_bp.route('/owner/menu/create', methods=['POST'])
@role_required(2)
def create_menu():
    try:
        # 1. Obtener datos del formulario
        restaurant_id = request.form.get('restaurant_id')
        dish_name = request.form.get('nombre')
        description = request.form.get('descripcion')
        price = request.form.get('precio')
        
        # 2. Manejo de la IMAGEN (Supabase)
        photo_file = request.files.get('foto')
        photo_url = None

        if photo_file and s3_client:
            try:
                # Generar nombre único: plato_uuid.jpg
                ext = photo_file.filename.rsplit('.', 1)[-1] if '.' in photo_file.filename else 'jpg'
                filename = f"platos/plato_{uuid.uuid4().hex}.{ext}"
                
                # Subir a Supabase
                s3_client.upload_fileobj(
                    photo_file,
                    S3_BUCKET,
                    filename,
                    ExtraArgs={'ContentType': photo_file.content_type}
                )
                # Construir URL pública
                photo_url = f"https://{SUPABASE_PROJECT}.supabase.co/storage/v1/object/public/{S3_BUCKET}/{filename}"
                print(f"Imagen subida: {photo_url}")
            except Exception as e:
                print(f"Error subiendo imagen: {e}")
                # No detenemos el proceso, se creará sin foto

        # 3. Guardar en Base de Datos
        # Convertimos precio a float
        try:
            price_float = float(price)
        except:
            return jsonify({'error': 'El precio debe ser un número'}), 400

        # Llamamos al servicio (que ya tiene el parámetro photo_url)
        OwnerService.create_menu(
            int(restaurant_id),
            dish_name,
            description,
            price_float,
            photo_url # <--- Aquí pasamos la URL generada
        )

        return jsonify({'message': 'Plato creado exitosamente', 'foto': photo_url}), 201

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Error creando plato: {str(e)}'}), 500

@owner_bp.route('/owner/menu/delete/<int:menu_id>', methods=['DELETE'])
@role_required(2)
def delete_menu(menu_id):
    try:
        if OwnerService.delete_menu(menu_id):
            return jsonify({'message': 'Plato eliminado'}), 200
        return jsonify({'error': 'No se pudo eliminar'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500