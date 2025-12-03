from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from SERVICES.authentication_service import AuthenticationService
from SERVICES.user_service import UserService
from UTILS.validators import parse_role_id
from config import Config

login_bp = Blueprint('login_bp', __name__)


@login_bp.route('/login')
def login():
    next_url = request.args.get('next')
    return render_template('VIEW/login.html', next=next_url)


@login_bp.route('/login/submit', methods=['POST'])
def login_submit():
    email = request.form.get('email')
    password = request.form.get('password')
    next_url = request.form.get('next')

    if not email or not password:
        flash('Email y contraseña son requeridos')
        return redirect(url_for('login_bp.login'))

    user = AuthenticationService.authenticate(email, password)

    if user:
        session_data = AuthenticationService.extract_session_data(user, email)
        session.update(session_data)

        flash(Config.SUCCESS_MESSAGES['login_success'])

        role = session.get('user_role')
        if AuthenticationService.is_admin(role):
            return redirect(url_for('user_bp.dashboard'))
        elif AuthenticationService.is_owner(role):
            return redirect(url_for('owner_bp.menus'))
        else:
            # Para clientes, mostrar inmediatamente el listado de menús con fotos
            return redirect(url_for('client_bp.menus'))
    else:
        flash(Config.ERROR_MESSAGES['invalid_credentials'])
        return redirect(url_for('login_bp.login'))


@login_bp.route('/register')
def register():
    return render_template('VIEW/register.html')


@login_bp.route('/register/submit', methods=['POST'])
def register_submit():
    name = request.form.get('name')
    lastname = request.form.get('lastname')
    email = request.form.get('email')
    password = request.form.get('password')
    role_id = parse_role_id(request.form.get('role'))

    try:
        UserService.create_user(name, lastname, email, password, role_id)
        flash(Config.SUCCESS_MESSAGES['registration_success'])
        return redirect(url_for('login_bp.login'))
    except ValueError as error:
        flash(f'Error de validación: {str(error)}')
        return redirect(url_for('login_bp.register'))
    except Exception as error:
        flash(f"{Config.ERROR_MESSAGES['registration_error']}: {str(error)}")
        return redirect(url_for('login_bp.register'))


@login_bp.route('/logout')
def logout():
    session.pop('user_email', None)
    session.pop('user_id', None)
    session.pop('user_role', None)
    session.pop('user_name', None)
    flash(Config.SUCCESS_MESSAGES['logout_success'])
    return redirect(url_for('login_bp.login'))


@login_bp.route('/reset-password')
def reset_password():
    return render_template('VIEW/reset_password.html')


@login_bp.route('/reset-password/submit', methods=['POST'])
def reset_password_submit():
    email = request.form.get('email')
    new_password = request.form.get('new_password')

    if not email or not new_password:
        flash('Email y contraseña son requeridos')
        return redirect(url_for('login_bp.reset_password'))

    try:
        UserService.update_password(email, new_password)
        flash(f"{Config.SUCCESS_MESSAGES['password_updated']} Ahora inicia sesión con la nueva contraseña.")
        return redirect(url_for('login_bp.login'))
    except ValueError as error:
        flash(f'Error de validación: {str(error)}')
        return redirect(url_for('login_bp.reset_password'))
    except Exception as error:
        flash(f"Error al actualizar contraseña: {str(error)}")
        return redirect(url_for('login_bp.reset_password'))
