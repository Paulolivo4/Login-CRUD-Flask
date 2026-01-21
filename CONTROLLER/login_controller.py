from flask import Blueprint, request, session, jsonify
from SERVICES.authentication_service import AuthenticationService
from config import Config
from repositories.azure_user_repository import AzureUserRepository
from SERVICES.email_service import EmailService
from werkzeug.security import generate_password_hash
import random

login_bp = Blueprint('login_bp', __name__)
repo = AzureUserRepository()

# ==========================================
# API PÚBLICA (SOLO JSON)
# ==========================================

@login_bp.route('/api/register', methods=['POST'])
def api_user_register():
    data = request.json
    email = data.get('email')
    
    if repo.get_user_by_email(email):
        return jsonify({'error': 'El correo ya está registrado'}), 400

    hashed_pw = generate_password_hash(data.get('password'))
    
    try:
        repo.create_user_from_registration(
            name=data.get('name'),
            lastname=data.get('lastname'),
            email=email,
            password=hashed_pw,
            role_id=3 
        )
        return jsonify({'message': 'Registro exitoso'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@login_bp.route('/api/forgot-password', methods=['POST'])
def api_forgot_password():
    email = request.json.get('email')
    user = repo.get_user_by_email(email)
    
    if not user:
        return jsonify({'error': 'No existe un usuario con ese correo'}), 404

    reset_code = str(random.randint(100000, 999999))
    # Asegúrate que EmailService maneje excepciones internamente o aquí
    try:
        EmailService.send_password_reset(email, user.NAME, reset_code)
        return jsonify({'message': 'Código de recuperación enviado'}), 200
    except Exception as e:
        return jsonify({'error': 'Error enviando correo'}), 500

@login_bp.route('/api/reset-password', methods=['POST'])
def api_reset_password():
    data = request.json
    email = data.get('email')
    code = data.get('code')
    new_password = data.get('newPassword')

    if not code or len(code) != 6:
        return jsonify({'error': 'Código de verificación inválido'}), 400

    try:
        hashed_pw = generate_password_hash(new_password)
        success = repo.update_user_password(email, hashed_pw)
        
        if success:
            return jsonify({'message': 'Contraseña actualizada correctamente'}), 200
        else:
            return jsonify({'error': 'No se pudo actualizar la contraseña'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@login_bp.route('/api/login', methods=['POST'])
def login_api():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Datos no enviados'}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email y contraseña requeridos'}), 400

    user = AuthenticationService.authenticate(email, password)

    if user:
        session_data = AuthenticationService.extract_session_data(user, email)
        session.update(session_data)
        
        # Patrón DTO implícito: Devolvemos solo lo que el front necesita
        return jsonify({
            'message': Config.SUCCESS_MESSAGES.get('login_success', 'Bienvenido'),
            'user': {
                'email': email,
                'role': session.get('user_role'),
                'name': session.get('user_name')
            }
        }), 200
    else:
        return jsonify({'error': Config.ERROR_MESSAGES.get('invalid_credentials', 'Credenciales incorrectas')}), 401

@login_bp.route('/api/check_session', methods=['GET'])
def check_session_api():
    user_id = session.get('user_id')
    if user_id:
        return jsonify({
            'authenticated': True,
            'user': {
                'email': session.get('user_email'),
                'role': session.get('user_role'),
                'name': session.get('user_name')
            }
        }), 200
    return jsonify({'authenticated': False}), 401

@login_bp.route('/api/logout', methods=['POST'])
def logout_api():
    session.clear() 
    return jsonify({'message': 'Sesión cerrada correctamente'}), 200