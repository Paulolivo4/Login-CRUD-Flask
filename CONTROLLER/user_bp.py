from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort

from SERVICES.user_service import UserService
from SERVICES.authentication_service import AuthenticationService
from UTILS.decorators import role_required
from UTILS.validators import parse_role_id
from config import Config

user_bp = Blueprint('user_bp', __name__, url_prefix='/users')


@user_bp.before_request
def require_login():
    if 'user_email' not in session:
        return redirect(url_for('login_bp.login', next=request.path))


# ============================================================================
# DASHBOARD - Role-based dashboard display
# ============================================================================

@user_bp.route('/dashboard')
def dashboard():
    role = session.get('user_role')

    if AuthenticationService.is_admin(role):
        try:
            users = UserService.get_all_users()
            return render_template('VIEW/admin_dashboard.html', usuarios=users)
        except Exception as error:
            flash(f"Error al cargar usuarios: {str(error)}")
            return render_template('VIEW/admin_dashboard.html', usuarios=[])

    elif AuthenticationService.is_owner(role):
        return render_template('VIEW/owner_dashboard.html')

    else:  # client
        return render_template('VIEW/client_dashboard.html')


# ============================================================================
# INDEX - List all users (Admin only)
# ============================================================================

@user_bp.route('/')
def index():
    if not AuthenticationService.is_admin(session.get('user_role')):
        abort(403)

    try:
        users = UserService.get_all_users()
        return render_template('VIEW/Index.html', usuarios=users)
    except Exception as error:
        flash(f"Error al cargar usuarios: {str(error)}")
        return render_template('VIEW/Index.html', usuarios=[])


# ============================================================================
# CREATE - Create a new user (Admin only)
# ============================================================================

@user_bp.route('/create', methods=['POST'])
def create_user():
    if not AuthenticationService.is_admin(session.get('user_role')):
        abort(403)

    name = request.form.get('name')
    lastname = request.form.get('lastname')
    email = request.form.get('email')
    password = request.form.get('password')
    role_id = parse_role_id(request.form.get('role'))

    if not all([name, lastname, email, password]):
        flash('Todos los campos son requeridos')
        return redirect(url_for('user_bp.index'))

    try:
        UserService.create_user(name, lastname, email, password, role_id)
        flash(Config.SUCCESS_MESSAGES['user_created'])
        return redirect(url_for('user_bp.index'))
    except ValueError as error:
        flash(f'Error de validación: {str(error)}')
        return redirect(url_for('user_bp.index'))
    except Exception as error:
        flash(f"Error al crear usuario: {str(error)}")
        return redirect(url_for('user_bp.index'))


# ============================================================================
# UPDATE - Update user password
# ============================================================================

@user_bp.route('/update', methods=['POST'])
def update_user():
    email = request.form.get('email')
    new_password = request.form.get('new_password')

    if not email or not new_password:
        flash('Email y contraseña son requeridos')
        return redirect(url_for('user_bp.index'))

    current_user_email = session.get('user_email')
    is_admin = AuthenticationService.is_admin(session.get('user_role'))

    if not is_admin and current_user_email != email:
        abort(403)

    try:
        UserService.update_password(email, new_password)
        flash(Config.SUCCESS_MESSAGES['user_updated'])
        return redirect(url_for('user_bp.index'))
    except ValueError as error:
        flash(f'Error de validación: {str(error)}')
        return redirect(url_for('user_bp.index'))
    except Exception as error:
        flash(f"Error al actualizar usuario: {str(error)}")
        return redirect(url_for('user_bp.index'))


# ============================================================================
# DELETE - Delete a user (Admin only)
# ============================================================================

@user_bp.route('/delete', methods=['POST'])
def delete_user():
    if not AuthenticationService.is_admin(session.get('user_role')):
        abort(403)

    email = request.form.get('email')

    if not email:
        flash('Email requerido')
        return redirect(url_for('user_bp.index'))

    try:
        UserService.delete_user(email)
        flash(Config.SUCCESS_MESSAGES['user_deleted'])
        return redirect(url_for('user_bp.index'))
    except ValueError as error:
        flash(f'Error de validación: {str(error)}')
        return redirect(url_for('user_bp.index'))
    except Exception as error:
        flash(f"Error al eliminar usuario: {str(error)}")
        return redirect(url_for('user_bp.index'))
