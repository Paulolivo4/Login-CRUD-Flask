from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from MODEL.client import ClientModel
from datetime import datetime

client_bp = Blueprint('client_bp', __name__, url_prefix='/client')


@client_bp.before_request
def require_client():
    # Solo clientes (rol 3) pueden acceder a estas rutas
    if 'user_email' not in session:
        return redirect(url_for('login_bp.login', next=request.path))
    role = session.get('user_role')
    if role not in (3, '3'):
        abort(403)


@client_bp.route('/reservations')
def reservations():
    user_id = session.get('user_id')
    reservas = ClientModel.list_reservations_by_client(user_id)
    return render_template('VIEW/client_reservations.html', reservas=reservas)


@client_bp.route('/reservations/create', methods=['POST'])
def create_reservation():
    user_id = session.get('user_id')
    try:
        id_restaurante = int(request.form.get('id_restaurante'))
        fecha_raw = request.form.get('fecha')
        personas = int(request.form.get('personas'))
        # Intentar parsear la fecha (inputs tipo datetime-local usan 'T' entre fecha y hora)
        if not fecha_raw:
            raise ValueError('Fecha requerida')
        try:
            # fromisoformat acepta 'YYYY-MM-DDTHH:MM' y variantes
            fecha = datetime.fromisoformat(fecha_raw)
        except Exception:
            # Intentar con reemplazo de T por espacio como fallback
            fecha = datetime.fromisoformat(fecha_raw.replace('T', ' '))
    except Exception as e:
        flash('Datos inválidos: ' + str(e))
        return redirect(url_for('client_bp.reservations'))

    # Rol del ejecutor es 3 (cliente)
    ClientModel.create_reservation(3, user_id, id_restaurante, fecha, personas)
    flash('Reserva creada correctamente')
    return redirect(url_for('client_bp.reservations'))


@client_bp.route('/reservations/delete', methods=['POST'])
def delete_reservation():
    try:
        id_reserva = int(request.form.get('id_reserva'))
    except Exception:
        flash('ID de reserva inválido')
        return redirect(url_for('client_bp.reservations'))
    # Rol del ejecutor es 3 (cliente)
    ClientModel.delete_reservation(3, id_reserva)
    flash('Reserva eliminada')
    return redirect(url_for('client_bp.reservations'))


@client_bp.route('/reservations/update', methods=['POST'])
def update_reservation():
    try:
        id_reserva = int(request.form.get('id_reserva'))
    except Exception:
        flash('ID de reserva inválido')
        return redirect(url_for('client_bp.reservations'))
    fecha_raw = request.form.get('fecha') or None
    personas = request.form.get('personas')
    personas = int(personas) if personas else None
    fecha = None
    if fecha_raw:
        try:
            fecha = datetime.fromisoformat(fecha_raw)
        except Exception:
            fecha = datetime.fromisoformat(fecha_raw.replace('T', ' '))
    ClientModel.update_reservation(id_reserva, fecha=fecha, personas=personas)
    flash('Reserva actualizada')
    return redirect(url_for('client_bp.reservations'))
