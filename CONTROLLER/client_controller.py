from flask import Blueprint, jsonify, request, session
from repositories.client_repository import ClientRepository
from SERVICES.email_service import EmailService # Importamos el servicio de email
from datetime import datetime

client_bp = Blueprint('client_bp', __name__, url_prefix='/api/client')
repo = ClientRepository()

@client_bp.route('/restaurants', methods=['GET'])
def get_restaurants():
    data = repo.get_all_restaurants()
    return jsonify(data), 200

@client_bp.route('/menu/<int:restaurant_id>', methods=['GET'])
def get_menu(restaurant_id):
    data = repo.get_menu_by_restaurant(restaurant_id)
    return jsonify(data), 200

@client_bp.route('/reserve', methods=['POST'])
def create_reservation():
    user_id = session.get('user_id')
    if not user_id: return jsonify({'error': 'No autorizado'}), 401

    data = request.json
    
    # Extraer datos incluyendo el correo real
    email_real = data.get('email_real') 
    restaurant_id = data.get('restaurant_id')
    menu_id = data.get('menu_id')
    menu_name = data.get('menu_name')
    reservation_date = data.get('date')
    people = data.get('people')
    total = data.get('total')
    card_brand = data.get('card_brand', 'Tarjeta')

    try:
        repo.create_reservation(
            user_id, restaurant_id, menu_id, reservation_date, people, total, f"TARJETA-{card_brand}"
        )

        # USAR EL CORREO REAL PARA EL ENVÍO
        EmailService.send_payment_confirmation(
            email_real, # <--- El correo que puso en el pago
            data.get('client_name', 'Cliente'), 
            menu_name, 
            total, 
            reservation_date, 
            f"Tarjeta {card_brand}"
        )

        return jsonify({'message': 'Reserva confirmada'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500