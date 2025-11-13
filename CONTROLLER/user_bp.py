from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from MODEL.User import User


user_bp = Blueprint('user_bp', __name__, url_prefix='/users')



@user_bp.before_request
def require_login_for_users():
    if 'user_email' not in session:
        return redirect(url_for('login_bp.login', next=request.path))

# -------------------------------
# READ - Mostrar lista de usuarios
# -------------------------------
@user_bp.route('/')
def index():
    
    role = session.get('user_role')
    if role not in (1, '1'):
        abort(403)
    usuarios = User.obtenerusuarios()
    return render_template('VIEW/Index.html', usuarios=usuarios)


@user_bp.route('/dashboard')
def dashboard():
    """Dashboard general que muestra una vista distinta según el rol del usuario."""
    role = session.get('user_role')
    
    if role in (1, '1'):
        usuarios = User.obtenerusuarios()
        return render_template('VIEW/admin_dashboard.html', usuarios=usuarios)
    elif role in (2, '2'):
        
        return render_template('VIEW/owner_dashboard.html')
    else:
        
        return render_template('VIEW/client_dashboard.html')

# -------------------------------
# CREATE - Crear un nuevo usuario
# ---------------------------------
@user_bp.route('/create', methods=['POST'])
def create_user():
    name = request.form['name']
    lastname = request.form['lastname']
    email = request.form['email']
    password = request.form['password']
    
    try:
        rol_id = int(request.form.get('role', 3))
    except Exception:
        rol_id = 3

    
    role = session.get('user_role')
    if role not in (1, '1'):
        abort(403)
    User.create_new_USER(name, lastname, email, password, rol_id=rol_id)
    flash("Usuario creado correctamente")
    return redirect(url_for('user_bp.index'))

# -------------------------------
# UPDATE - Actualizar un usuario
# -------------------------------
@user_bp.route('/update', methods=['POST'])
def update_user():
    email = request.form['email']
    new_password = request.form['new_password']
    role = session.get('user_role')
    current_email = session.get('user_email')
    if role in (1, '1') or current_email == email:
        User.update_user(email, new_password)
    else:
        abort(403)
    flash("Usuario actualizado correctamente")
    return redirect(url_for('user_bp.index'))

# -------------------------------
# DELETE - Eliminar un usuario
# -------------------------------
@user_bp.route('/delete', methods=['POST'])
def delete_user():
    email = request.form['email']
    role = session.get('user_role')
    if role not in (1, '1'):
        abort(403)
    User.delete_user(email)
    flash("Usuario eliminado correctamente")
    return redirect(url_for('user_bp.index'))
