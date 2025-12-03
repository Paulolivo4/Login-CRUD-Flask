from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort, jsonify

from SERVICES.owner_service import OwnerService
from SERVICES.authentication_service import AuthenticationService
from UTILS.validators import parse_integer, parse_float
from config import Config
import json
import os
import logging
import boto3
from botocore.config import Config as BConfig
import uuid

owner_bp = Blueprint('owner_bp', __name__, url_prefix='/owner')


# Configuración S3 (leer de variables de entorno para mayor seguridad)
S3_BUCKET = os.environ.get('SUPABASE_S3_BUCKET', 'fotos')
S3_ENDPOINT = os.environ.get('SUPABASE_S3_ENDPOINT', 'https://bljzxhufvyectslxmzrr.storage.supabase.co')
# Proyecto/ref público para construir la URL pública (si no lo proporcionas, usamos el valor conocido)
SUPABASE_PROJECT = os.environ.get('SUPABASE_PROJECT_REF', 'bljzxhufvyectslxmzrr')
S3_REGION = os.environ.get('SUPABASE_S3_REGION', 'us-east-1')
AWS_ACCESS_KEY_ID = os.environ.get('SUPABASE_S3_KEY')
AWS_SECRET_ACCESS_KEY = os.environ.get('SUPABASE_S3_SECRET')

logger = logging.getLogger(__name__)

if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    logger.warning('No se han encontrado credenciales S3 en variables de entorno (SUPABASE_S3_KEY / SUPABASE_S3_SECRET). Las subidas fallarán hasta configurarlas.')

try:
    s3 = boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=S3_REGION,
        config=BConfig(signature_version='s3v4'),
    )
except Exception as e:
    s3 = None
    logger.exception('Error al inicializar el cliente S3: %s', e)


@owner_bp.before_request
def require_owner():
    if 'user_email' not in session:
        return redirect(url_for('login_bp.login', next=request.path))

    if not AuthenticationService.is_owner(session.get('user_role')):
        abort(403)


# ============================================================================
# DASHBOARD - Owner dashboard
# ============================================================================

@owner_bp.route('/dashboard')
def dashboard():
    return render_template('VIEW/owner_dashboard.html')


# ============================================================================
# READ - List owner menus
# ============================================================================

@owner_bp.route('/menus')
def menus():
    owner_id = session.get('user_id')

    try:
        menus_list = OwnerService.get_menus(owner_id)
        # Obtener restaurante del owner para el formulario
        owner_restaurant = OwnerService.get_owner_restaurant(owner_id)
        return render_template('VIEW/owner_menus.html', menus=menus_list, restaurant=owner_restaurant)
    except Exception as error:
        flash(f"Error al cargar menús: {str(error)}")
        return render_template('VIEW/owner_menus.html', menus=[], restaurant=None)


# ============================================================================
# CREATE - Create a new menu item
# ============================================================================

@owner_bp.route('/menus/create', methods=['POST'])
def create_menu():
    restaurant_id = parse_integer(request.form.get('id_restaurante'))
    dish_name = request.form.get('nombre')
    description = request.form.get('descripcion')
    price = parse_float(request.form.get('precio'))
    # validar campos básicos
    if not all([restaurant_id, dish_name, description, price]):
        flash('Todos los campos son requeridos')
        return redirect(url_for('owner_bp.menus'))

    # manejar upload de imagen opcional (campo 'photo')
    photo_file = request.files.get('photo')
    photo_url = None

    try:
        if photo_file and getattr(photo_file, 'filename', ''):
            orig = photo_file.filename
            ext = orig.rsplit('.', 1)[-1] if '.' in orig else ''
            file_name = f"menu_{uuid.uuid4().hex}.{ext}" if ext else f"menu_{uuid.uuid4().hex}"
            try:
                if s3 is None:
                    raise RuntimeError('Cliente S3 no inicializado. Configure SUPABASE_S3_KEY y SUPABASE_S3_SECRET en variables de entorno.')
                s3.upload_fileobj(photo_file, S3_BUCKET, file_name)
                photo_url = f"https://{SUPABASE_PROJECT}.supabase.co/storage/v1/object/public/{S3_BUCKET}/{file_name}"
            except Exception as up_err:
                logger.exception('Fallo al subir imagen a S3: %s', up_err)
                flash(f"Error al subir la imagen: {str(up_err)}")
                return redirect(url_for('owner_bp.menus'))

        OwnerService.create_menu(restaurant_id, dish_name, description, price, photo_url)
        flash(Config.SUCCESS_MESSAGES['menu_created'])
        return redirect(url_for('owner_bp.menus'))
    except ValueError as error:
        flash(f'Error de validación: {str(error)}')
        return redirect(url_for('owner_bp.menus'))
    except Exception as error:
        flash(f"Error al crear menú: {str(error)}")
        return redirect(url_for('owner_bp.menus'))


# ============================================================================
# UPDATE - Update an existing menu item
# ============================================================================

@owner_bp.route('/menus/edit', methods=['POST'])
def edit_menu():
    menu_id = parse_integer(request.form.get('id_menu'))
    dish_name = request.form.get('nombre')
    description = request.form.get('descripcion')
    price = parse_float(request.form.get('precio'))
    if not all([menu_id, dish_name, description, price]):
        flash('Todos los campos son requeridos')
        return redirect(url_for('owner_bp.menus'))

    # manejar upload de imagen opcional
    photo_file = request.files.get('photo')
    photo_url = None

    try:
        if photo_file and getattr(photo_file, 'filename', ''):
            orig = photo_file.filename
            ext = orig.rsplit('.', 1)[-1] if '.' in orig else ''
            file_name = f"menu_{uuid.uuid4().hex}.{ext}" if ext else f"menu_{uuid.uuid4().hex}"
            try:
                if s3 is None:
                    raise RuntimeError('Cliente S3 no inicializado. Configure SUPABASE_S3_KEY y SUPABASE_S3_SECRET en variables de entorno.')
                s3.upload_fileobj(photo_file, S3_BUCKET, file_name)
                photo_url = f"https://{SUPABASE_PROJECT}.supabase.co/storage/v1/object/public/{S3_BUCKET}/{file_name}"
            except Exception as up_err:
                logger.exception('Fallo al subir imagen a S3: %s', up_err)
                flash(f"Error al subir la imagen: {str(up_err)}")
                return redirect(url_for('owner_bp.menus'))

        OwnerService.update_menu(menu_id, dish_name, description, price, photo_url)
        flash(Config.SUCCESS_MESSAGES['menu_updated'])
        return redirect(url_for('owner_bp.menus'))
    except ValueError as error:
        flash(f'Error de validación: {str(error)}')
        return redirect(url_for('owner_bp.menus'))
    except Exception as error:
        flash(f"Error al actualizar menú: {str(error)}")
        return redirect(url_for('owner_bp.menus'))


# ============================================================================
# DELETE - Delete a menu item
# ============================================================================

@owner_bp.route('/menus/delete', methods=['POST'])
def delete_menu():
    menu_id = parse_integer(request.form.get('id_menu'))

    if not menu_id:
        flash('ID de menú inválido')
        return redirect(url_for('owner_bp.menus'))

    try:
        OwnerService.delete_menu(menu_id)
        flash(Config.SUCCESS_MESSAGES['menu_deleted'])
        return redirect(url_for('owner_bp.menus'))
    except ValueError as error:
        flash(f'Error de validación: {str(error)}')
        return redirect(url_for('owner_bp.menus'))
    except Exception as error:
        flash(f"Error al eliminar menú: {str(error)}")
        return redirect(url_for('owner_bp.menus'))

