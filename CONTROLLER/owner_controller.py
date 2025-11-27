from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort

from SERVICES.owner_service import OwnerService
from SERVICES.authentication_service import AuthenticationService
from UTILS.validators import parse_integer, parse_float
from config import Config

owner_bp = Blueprint('owner_bp', __name__, url_prefix='/owner')


@owner_bp.before_request
def require_owner():
    if 'user_email' not in session:
        return redirect(url_for('login_bp.login', next=request.path))

    if not AuthenticationService.is_owner(session.get('user_role')):
        abort(403)


# ============================================================================
# READ - List owner menus
# ============================================================================

@owner_bp.route('/menus')
def menus():
    owner_id = session.get('user_id')

    try:
        menus_list = OwnerService.get_menus(owner_id)
        return render_template('VIEW/owner_menus.html', menus=menus_list)
    except Exception as error:
        flash(f"Error al cargar menús: {str(error)}")
        return render_template('VIEW/owner_menus.html', menus=[])


# ============================================================================
# CREATE - Create a new menu item
# ============================================================================

@owner_bp.route('/menus/create', methods=['POST'])
def create_menu():
    restaurant_id = parse_integer(request.form.get('id_restaurante'))
    dish_name = request.form.get('nombre')
    description = request.form.get('descripcion')
    price = parse_float(request.form.get('precio'))

    if not all([restaurant_id, dish_name, description, price]):
        flash('Todos los campos son requeridos')
        return redirect(url_for('owner_bp.menus'))

    try:
        OwnerService.create_menu(restaurant_id, dish_name, description, price)
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

    try:
        OwnerService.update_menu(menu_id, dish_name, description, price)
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

