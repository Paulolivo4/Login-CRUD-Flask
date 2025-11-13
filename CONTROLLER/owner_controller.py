from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from MODEL.owner_restaurant import OwnerModel

owner_bp = Blueprint('owner_bp', __name__, url_prefix='/owner')


@owner_bp.before_request
def require_owner():
    # Solo dueños (rol 2) pueden acceder
    if 'user_email' not in session:
        return redirect(url_for('login_bp.login', next=request.path))
    role = session.get('user_role')
    if role not in (2, '2'):
        abort(403)


@owner_bp.route('/menus')
def menus():
    owner_id = session.get('user_id')
    menus = OwnerModel.list_menus_by_owner(owner_id)
    return render_template('VIEW/owner_menus.html', menus=menus)


@owner_bp.route('/menus/create', methods=['POST'])
def create_menu():
    try:
        id_restaurante = int(request.form.get('id_restaurante'))
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        precio = float(request.form.get('precio'))
    except Exception as e:
        flash('Datos inválidos: ' + str(e))
        return redirect(url_for('owner_bp.menus'))

    OwnerModel.create_menu(2, id_restaurante, nombre, descripcion, precio)
    flash('Menú creado')
    return redirect(url_for('owner_bp.menus'))


@owner_bp.route('/menus/edit', methods=['POST'])
def edit_menu():
    try:
        id_menu = int(request.form.get('id_menu'))
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        precio = float(request.form.get('precio'))
    except Exception as e:
        flash('Datos inválidos: ' + str(e))
        return redirect(url_for('owner_bp.menus'))

    OwnerModel.edit_menu(2, id_menu, nombre, descripcion, precio)
    flash('Menú actualizado')
    return redirect(url_for('owner_bp.menus'))


@owner_bp.route('/menus/delete', methods=['POST'])
def delete_menu():
    try:
        id_menu = int(request.form.get('id_menu'))
    except Exception:
        flash('ID inválido')
        return redirect(url_for('owner_bp.menus'))
    OwnerModel.delete_menu(2, id_menu)
    flash('Menú eliminado')
    return redirect(url_for('owner_bp.menus'))

