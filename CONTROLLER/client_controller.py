from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort, jsonify

from SERVICES.client_service import ClientService
from SERVICES.authentication_service import AuthenticationService
from UTILS.validators import parse_datetime, parse_integer, parse_float
from config import Config

client_bp = Blueprint('client_bp', __name__, url_prefix='/client')


@client_bp.before_request
def require_client():
    if 'user_email' not in session:
        return redirect(url_for('login_bp.login', next=request.path))

    if not AuthenticationService.is_client(session.get('user_role')):
        abort(403)


# ============================================================================
# READ - List all available menus for browsing
# ============================================================================

@client_bp.route('/menus')
def menus():
    try:
        menus_list = ClientService.get_all_menus()
        return render_template('VIEW/client_menus.html', menus=menus_list)
    except Exception as error:
        flash(f"Error al cargar menús: {str(error)}")
        return render_template('VIEW/client_menus.html', menus=[])


@client_bp.route('/menus/detail/<int:menu_id>')
def menu_detail(menu_id):
    """API que retorna detalle de un menú en JSON."""
    try:
        menu = ClientService.get_menu_detail(menu_id)
        if not menu:
            return jsonify({'error': 'Menú no encontrado'}), 404
        return jsonify(menu)
    except Exception as error:
        return jsonify({'error': str(error)}), 500


# ============================================================================
# READ - List client reservations
# ============================================================================

@client_bp.route('/reservations')
def reservations():
    client_id = session.get('user_id')

    try:
        reservations_list = ClientService.get_reservations(client_id)
        restaurants_list = ClientService.get_available_restaurants()
        return render_template('VIEW/client_reservations.html', reservas=reservations_list, restaurants=restaurants_list)
    except Exception as error:
        flash(f"Error al cargar reservas: {str(error)}")
        return render_template('VIEW/client_reservations.html', reservas=[], restaurants=[])


# ============================================================================
# CREATE - Create a new reservation
# ============================================================================

@client_bp.route('/reservations/create', methods=['POST'])
def create_reservation():
    client_id = session.get('user_id')

    # Parse and validate restaurant ID
    restaurant_id = parse_integer(request.form.get('id_restaurante'))
    if not restaurant_id:
        flash('ID de restaurante inválido')
        return redirect(url_for('client_bp.reservations'))

    # Parse and validate reservation date
    date_success, reservation_date = parse_datetime(request.form.get('fecha'))
    if not date_success:
        flash('Fecha y hora inválidas')
        return redirect(url_for('client_bp.reservations'))

    # Parse and validate number of people
    number_of_people = parse_integer(request.form.get('personas'))
    if not number_of_people:
        flash('Cantidad de personas inválida')
        return redirect(url_for('client_bp.reservations'))

    try:
        ClientService.create_reservation(client_id, restaurant_id, reservation_date, number_of_people)
        flash(Config.SUCCESS_MESSAGES['reservation_created'])
        return redirect(url_for('client_bp.reservations'))
    except ValueError as error:
        flash(f'Error de validación: {str(error)}')
        return redirect(url_for('client_bp.reservations'))
    except Exception as error:
        flash(f"Error al crear reserva: {str(error)}")
        return redirect(url_for('client_bp.reservations'))


# ============================================================================
# UPDATE - Update an existing reservation
# ============================================================================

@client_bp.route('/reservations/update', methods=['POST'])
def update_reservation():
    reservation_id = parse_integer(request.form.get('id_reserva'))
    if not reservation_id:
        flash('ID de reserva inválido')
        return redirect(url_for('client_bp.reservations'))

    # Parse optional reservation date
    reservation_date = None
    fecha_raw = request.form.get('fecha')
    if fecha_raw:
        date_success, reservation_date = parse_datetime(fecha_raw)
        if not date_success:
            flash('Fecha y hora inválidas')
            return redirect(url_for('client_bp.reservations'))

    # Parse optional number of people
    number_of_people = parse_integer(request.form.get('personas'))

    try:
        ClientService.update_reservation(reservation_id, reservation_date, number_of_people)
        flash(Config.SUCCESS_MESSAGES['reservation_updated'])
        return redirect(url_for('client_bp.reservations'))
    except ValueError as error:
        flash(f'Error de validación: {str(error)}')
        return redirect(url_for('client_bp.reservations'))
    except Exception as error:
        flash(f"Error al actualizar reserva: {str(error)}")
        return redirect(url_for('client_bp.reservations'))


# ============================================================================
# DELETE - Delete a reservation
# ============================================================================

@client_bp.route('/reservations/delete', methods=['POST'])
def delete_reservation():
    reservation_id = parse_integer(request.form.get('id_reserva'))
    if not reservation_id:
        flash('ID de reserva inválido')
        return redirect(url_for('client_bp.reservations'))

    try:
        ClientService.delete_reservation(reservation_id)
        flash(Config.SUCCESS_MESSAGES['reservation_deleted'])
        return redirect(url_for('client_bp.reservations'))
    except ValueError as error:
        flash(f'Error de validación: {str(error)}')
        return redirect(url_for('client_bp.reservations'))
    except Exception as error:
        flash(f"Error al eliminar reserva: {str(error)}")
        return redirect(url_for('client_bp.reservations'))
