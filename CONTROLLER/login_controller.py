from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from MODEL.User import User

login_bp = Blueprint('login_bp', __name__)


@login_bp.route('/login')
def login():
    # Pasar parámetro 'next' si existe para redirigir después del login
    next_url = request.args.get('next')
    return render_template('VIEW/login.html', next=next_url)


@login_bp.route('/login/submit', methods=['POST'])
def login_submit():
    email = request.form.get('email')
    password = request.form.get('password')
    next_url = request.form.get('next')
    if User.authenticate(email, password):
        session['user_email'] = email
        flash('Has iniciado sesión correctamente')
        # Si se proporcionó next y parece seguro (ruta interna), redirigir ahí
        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        return redirect(url_for('user_bp.index'))
    else:
        flash('Credenciales inválidas')
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
    # Crear usuario en BD
    try:
        User.create_new_USER(name, lastname, email, password)
        flash('Usuario registrado correctamente. Ahora puedes iniciar sesión.')
        return redirect(url_for('login_bp.login'))
    except Exception as e:
        flash('Error al registrar usuario: ' + str(e))
        return redirect(url_for('login_bp.register'))


@login_bp.route('/logout')
def logout():
    session.pop('user_email', None)
    flash('Has cerrado sesión')
    return redirect(url_for('login_bp.login'))


@login_bp.route('/reset-password')
def reset_password():
    # Mostrar formulario para restablecer contraseña (público)
    return render_template('VIEW/reset_password.html')


@login_bp.route('/reset-password/submit', methods=['POST'])
def reset_password_submit():
    email = request.form.get('email')
    new_password = request.form.get('new_password')
    try:
        User.update_user(email, new_password)
        flash('Contraseña actualizada correctamente. Ahora inicia sesión con la nueva contraseña.')
        return redirect(url_for('login_bp.login'))
    except Exception as e:
        flash('Error al actualizar contraseña: ' + str(e))
        return redirect(url_for('login_bp.reset_password'))
