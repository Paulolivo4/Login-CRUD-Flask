from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from MODEL.User import User

# Definimos el Blueprint
user_bp = Blueprint('user_bp', __name__, url_prefix='/users')  # opcional url_prefix

# Protege todas las rutas bajo /users/ para que solo usuarios autenticados accedan
@user_bp.before_request
def require_login_for_users():
    if 'user_email' not in session:
        abort(403)

# -------------------------------
# READ - Mostrar lista de usuarios
# -------------------------------
@user_bp.route('/')
def index():
    usuarios = User.obtenerusuarios()
    return render_template('VIEW/Index.html', usuarios=usuarios)

# -------------------------------
# CREATE - Crear un nuevo usuario
# -------------------------------
@user_bp.route('/create', methods=['POST'])
def create_user():
    name = request.form['name']
    lastname = request.form['lastname']
    email = request.form['email']
    password = request.form['password']

    User.create_new_USER(name, lastname, email, password)
    flash("Usuario creado correctamente")
    return redirect(url_for('user_bp.index'))

# -------------------------------
# UPDATE - Actualizar un usuario
# -------------------------------
@user_bp.route('/update', methods=['POST'])
def update_user():
    email = request.form['email']
    new_password = request.form['new_password']

    User.update_user(email, new_password)
    flash("Usuario actualizado correctamente")
    return redirect(url_for('user_bp.index'))

# -------------------------------
# DELETE - Eliminar un usuario
# -------------------------------
@user_bp.route('/delete', methods=['POST'])
def delete_user():
    email = request.form['email']

    User.delete_user(email)
    flash("Usuario eliminado correctamente")
    return redirect(url_for('user_bp.index'))
