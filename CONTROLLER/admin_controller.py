from flask import Blueprint, request, jsonify, session
from SERVICES.admin_service import AdminService
from SERVICES.authentication_service import AuthenticationService
from config import Config
import os
import logging
import boto3
from botocore.config import Config as BConfig
import uuid

# Configuración de Logging
logger = logging.getLogger(__name__)

# Definimos el Blueprint
admin_bp = Blueprint('admin_bp', __name__, url_prefix='/api/admin')

# ----------------------------------------------------------------------------
# CONFIGURACIÓN S3 (SUPABASE STORAGE)
# ----------------------------------------------------------------------------
# Reutilizamos las mismas variables de entorno que tienes en owner_controller
S3_BUCKET = os.environ.get('SUPABASE_S3_BUCKET', 'restaurantes') # Ojo: Bucket diferente o el mismo 'fotos'
S3_ENDPOINT = os.environ.get('SUPABASE_S3_ENDPOINT', 'https://bljzxhufvyectslxmzrr.storage.supabase.co')
SUPABASE_PROJECT = os.environ.get('SUPABASE_PROJECT_REF', 'bljzxhufvyectslxmzrr')
S3_REGION = os.environ.get('SUPABASE_S3_REGION', 'us-east-1')
AWS_ACCESS_KEY_ID = os.environ.get('SUPABASE_S3_KEY')
AWS_SECRET_ACCESS_KEY = os.environ.get('SUPABASE_S3_SECRET')

# Inicializar cliente S3
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
        logger.exception(f'Error al inicializar S3 en Admin: {e}')
else:
    logger.warning('Credenciales S3 no encontradas en Admin Controller.')

# ----------------------------------------------------------------------------
# MIDDLEWARE DE SEGURIDAD
# ----------------------------------------------------------------------------
@admin_bp.before_request
def require_admin():
    # Si es una petición OPTIONS (pre-flight de CORS), la dejamos pasar
    if request.method == 'OPTIONS':
        return
        
    if 'user_email' not in session:
        return jsonify({'error': 'No has iniciado sesión'}), 401

    role = session.get('user_role')
    if not AuthenticationService.is_admin(role):
        return jsonify({'error': 'Acceso denegado. Se requiere ser Administrador'}), 403

# ----------------------------------------------------------------------------
# ENDPOINTS
# ----------------------------------------------------------------------------

@admin_bp.route('/restaurants', methods=['GET'])
def restaurants_api():
    try:
        restaurants_list = AdminService.get_all_restaurants()
        
        # Serializar datos para JSON
        data = []
        for r in restaurants_list:
            # Ajusta según si r es tupla o dict
            # Estructura Tupla esperada: (ID, EMAIL_DUENO, NOMBRE, DIRECCION, TELEFONO, OPENING, CLOSING, LOGO)
            item = {
                'id': r[0] if isinstance(r, tuple) else r.get('ID'),
                'email_dueno': r[1] if isinstance(r, tuple) else r.get('EMAIL_DUENO'),
                'nombre': r[2] if isinstance(r, tuple) else r.get('NAME'),
                'direccion': r[3] if isinstance(r, tuple) else r.get('ADDRESS'),
                'telefono': r[4] if isinstance(r, tuple) else r.get('PHONE'),
                # Si agregaste las columnas, vendrán aquí. Si no, usa valores por defecto.
                'horario': f"{r[5]} - {r[6]}" if isinstance(r, tuple) and len(r)>6 else "No definido",
                'logo_url': r[7] if isinstance(r, tuple) and len(r)>7 else None
            }
            data.append(item)
            
        return jsonify(data), 200
    except Exception as error:
        print(f"Error cargando restaurantes: {error}")
        return jsonify({'error': 'Error interno', 'details': str(error)}), 500

@admin_bp.route('/restaurants/create', methods=['POST'])
def create_restaurant_api():
    # 1. Recibir datos del formulario
    owner_id = request.form.get('id_dueno')
    name = request.form.get('nombre')
    address = request.form.get('direccion')
    phone = request.form.get('telefono')
    opening = request.form.get('horario_apertura')
    closing = request.form.get('horario_cierre')

    # Validaciones básicas
    if not all([owner_id, name, address, phone]):
        return jsonify({'error': 'Faltan campos obligatorios'}), 400

    # ---------------------------------------------------------
    # CORRECCIÓN AQUÍ: Inicializar logo_url antes del IF
    # ---------------------------------------------------------
    logo_file = request.files.get('logo')
    logo_url = None  # <--- ¡ESTA LÍNEA ES LA CLAVE! (Evita el error de variable indefinida)

    # Solo intentamos subir si hay archivo y cliente S3 configurado
    if logo_file and s3_client:
        try:
            ext = logo_file.filename.rsplit('.', 1)[-1] if '.' in logo_file.filename else 'jpg'
            clean_name = name.replace(' ', '_').lower()
            file_key = f"logos/{clean_name}_{uuid.uuid4().hex}.{ext}"
            
            s3_client.upload_fileobj(
                logo_file, 
                S3_BUCKET, 
                file_key,
                ExtraArgs={'ContentType': logo_file.content_type}
            )
            
            logo_url = f"https://{SUPABASE_PROJECT}.supabase.co/storage/v1/object/public/{S3_BUCKET}/{file_key}"
            
        except Exception as e:
            logger.error(f"Error subiendo logo a S3: {e}")
            # Si falla la subida, podemos decidir si parar o seguir sin logo. 
            # Aquí seguimos, pero logo_url se queda como None o lo que tenga.
            return jsonify({'error': 'Error al subir el logo, intente de nuevo'}), 500

    try:
        # 2. Guardar en Base de Datos
        # Ahora logo_url siempre existe (es una URL o es None)
        AdminService.create_restaurant(
            owner_id, 
            name, 
            address, 
            phone, 
            opening, 
            closing, 
            logo_url 
        )
        
        return jsonify({'message': 'Restaurante creado exitosamente'}), 201
        
    except ValueError as error:
        return jsonify({'error': str(error)}), 400
    except Exception as error:
        logger.error(f"Error BD creando restaurante: {error}")
        return jsonify({'error': 'Error interno al guardar en base de datos'}), 500