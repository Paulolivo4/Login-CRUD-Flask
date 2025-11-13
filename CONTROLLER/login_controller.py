from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from MODEL.users import User

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
    user = User.authenticate(email, password)
    if user:
        # Guardar información mínima en sesión (soportar distintos nombres de columna)
        def pick(u, *keys):
            for k in keys:
                if isinstance(u, dict) and k in u and u[k] is not None:
                    return u[k]
            return None

        session['user_email'] = pick(user, 'EMAIL', 'Email', 'email') or email
        session['user_id'] = pick(user, 'ID', 'Id', 'id')
        # Algunos SP/consultas pueden devolver ROL_ID o ROL u otras variantes
        session['user_role'] = pick(user, 'ROL_ID', 'ROL', 'Rol', 'rol_id', 'rol')
        session['user_name'] = pick(user, 'NAME', 'Name', 'name')
        flash('Has iniciado sesión correctamente')
        
        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        # Redirigir según rol: 1=admin, 2=dueño, 3=cliente
        role = session.get('user_role')
        if role in (1, '1'):
            return redirect(url_for('user_bp.dashboard'))
        if role in (2, '2'):
            return redirect(url_for('owner_bp.menus'))
        # Por defecto o rol 3 -> cliente
        return redirect(url_for('client_bp.reservations'))
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
    try:
        rol_raw = request.form.get('role')
        rol_id = int(rol_raw) if rol_raw is not None else 3
    except Exception:
        rol_id = 3
    try:
        User.create_new_USER(name, lastname, email, password, rol_id=rol_id)
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
