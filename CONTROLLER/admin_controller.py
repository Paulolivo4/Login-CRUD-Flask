from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort

from SERVICES.admin_service import AdminService
from SERVICES.authentication_service import AuthenticationService
from config import Config

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')


@admin_bp.before_request
def require_admin():
    if 'user_email' not in session:
        return redirect(url_for('login_bp.login', next=request.path))

    if not AuthenticationService.is_admin(session.get('user_role')):
        abort(403)


# ============================================================================
# READ - List all restaurants
# ============================================================================

@admin_bp.route('/restaurants')
def restaurants():
    try:
        restaurants_list = AdminService.get_all_restaurants()
        return render_template('VIEW/admin_create_restaurant.html', restaurantes=restaurants_list)
    except Exception as error:
        flash(f"Error al cargar restaurantes: {str(error)}")
        return render_template('VIEW/admin_create_restaurant.html', restaurantes=[])


# ============================================================================
# CREATE - Create a new restaurant
# ============================================================================

@admin_bp.route('/restaurants/create', methods=['POST'])
def create_restaurant():
    owner_email = request.form.get('email_dueno')
    name = request.form.get('nombre')
    address = request.form.get('direccion')
    phone = request.form.get('telefono')

    # Validate required fields
    if not all([owner_email, name, address, phone]):
        flash('Completa los campos requeridos')
        return redirect(url_for('admin_bp.restaurants'))

    try:
        AdminService.create_restaurant(owner_email, name, address, phone)
        flash(Config.SUCCESS_MESSAGES['restaurant_created'])
        return redirect(url_for('admin_bp.restaurants'))
    except ValueError as error:
        flash(f'Error de validación: {str(error)}')
        return redirect(url_for('admin_bp.restaurants'))
    except Exception as error:
        flash(f"Error al crear restaurante: {str(error)}")
        return redirect(url_for('admin_bp.restaurants'))
