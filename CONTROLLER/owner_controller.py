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

# --- CONFIGURACIÓN SUPABASE (Para subir las fotos) ---
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

# --- RUTA DASHBOARD (La que te daba error 500) ---
@owner_bp.route('/owner/dashboard-data', methods=['GET'])
@role_required(2)
def get_dashboard_data():
    user_id = session.get('user_id')
    try:
        # Ahora esto funcionará porque agregamos get_owner_stats al servicio
        stats = OwnerService.get_owner_stats(user_id)
        if 'error' in stats: return jsonify(stats), 400
        
        restaurant = OwnerService.get_owner_restaurant(user_id)
        restaurant_id = restaurant[0] if restaurant else None
        
        menus_list = OwnerService.get_menus(user_id)
        
        # Formatear menús
        menus_data = []
        if menus_list:
            for m in menus_list:
                menus_data.append({
                    'id': m[0],
                    'restaurant_id': m[1],
                    'nombre': m[2],
                    'descripcion': m[3],
                    'precio': float(m[4]),
                    'disponible': m[5],
                    'foto': m[6] # Aquí vendrá la URL de Supabase
                })
        
        # Obtener reservas
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
            ).join(LoginDetails, Reserva.ID_CLIENTE == LoginDetails.ID)\
             .filter(Reserva.ID_RESTAURANTE == restaurant_id).all()
            
            for res in reservations:
                reservations_data.append({
                    'id': res.ID_RESERVA,
                    'cliente': f"{res.cliente_nombre} {res.cliente_apellido}",
                    'fecha': str(res.FECHA_RESERVA),
                    'personas': res.CANTIDAD_PERSONAS,
                    'plato': 'Reserva General',
                    'metodo_pago': 'Tarjeta',
                    'estado': res.ESTADO,
                    'total': float(res.CANTIDAD_PERSONAS * 15.0) # Cálculo seguro
                })

        return jsonify({
            'restaurant': {'id': restaurant_id, 'nombre': restaurant[1] if restaurant else 'Sin nombre'},
            'menus': menus_data,
            'reservations': reservations_data,
            'stats': stats
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# --- RUTA CREAR MENU (Con subida de fotos arreglada) ---
@owner_bp.route('/owner/menu/create', methods=['POST'])
@role_required(2)
def create_menu():
    try:
        restaurant_id = request.form.get('restaurant_id')
        dish_name = request.form.get('nombre')
        description = request.form.get('descripcion')
        price = request.form.get('precio')
        
        # SUBIDA DE IMAGEN A SUPABASE
        photo_file = request.files.get('foto')
        photo_url = None

        if photo_file and s3_client:
            try:
                ext = photo_file.filename.rsplit('.', 1)[-1] if '.' in photo_file.filename else 'jpg'
                filename = f"platos/plato_{uuid.uuid4().hex}.{ext}"
                s3_client.upload_fileobj(
                    photo_file, S3_BUCKET, filename,
                    ExtraArgs={'ContentType': photo_file.content_type}
                )
                photo_url = f"https://{SUPABASE_PROJECT}.supabase.co/storage/v1/object/public/{S3_BUCKET}/{filename}"
            except Exception as e:
                logger.error(f"Error subiendo imagen: {e}")

        OwnerService.create_menu(
            int(restaurant_id), dish_name, description, float(price), photo_url
        )

        return jsonify({'message': 'Plato creado exitosamente', 'foto': photo_url}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@owner_bp.route('/owner/menu/delete/<int:menu_id>', methods=['DELETE'])
@role_required(2)
def delete_menu(menu_id):
    try:
        OwnerService.delete_menu(menu_id)
        return jsonify({'message': 'Eliminado'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500