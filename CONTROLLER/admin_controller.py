from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from MODEL.admin_restaurant import AdminRestaurantModel

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')


@admin_bp.before_request
def require_admin():
    if 'user_email' not in session:
        return redirect(url_for('login_bp.login', next=request.path))
    role = session.get('user_role')
    if role not in (1, '1'):
        abort(403)


@admin_bp.route('/restaurants')
def restaurants():
    # Mostrar formulario y lista de restaurantes
    restaurantes = AdminRestaurantModel.list_restaurants()
    return render_template('VIEW/admin_create_restaurant.html', restaurantes=restaurantes)


@admin_bp.route('/restaurants/create', methods=['POST'])
def create_restaurant():
    # admin_email tomado de la sesión
    admin_email = session.get('user_email')
    email_dueno = request.form.get('email_dueno')
    nombre = request.form.get('nombre')
    direccion = request.form.get('direccion')
    telefono = request.form.get('telefono')

    if not (email_dueno and nombre):
        flash('Completa los campos requeridos')
        return redirect(url_for('admin_bp.restaurants'))

    try:
        AdminRestaurantModel.create_restaurant(admin_email, email_dueno, nombre, direccion, telefono)
        flash('Restaurante creado (o mensaje desde SP).')
    except Exception as e:
        flash('Error al crear restaurante: ' + str(e))

    return redirect(url_for('admin_bp.restaurants'))
