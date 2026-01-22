from flask import Blueprint, request, session, jsonify
from SERVICES.authentication_service import AuthenticationService
from config import Config
from repositories.azure_user_repository import AzureUserRepository
from SERVICES.email_service import EmailService
from werkzeug.security import generate_password_hash
import random
import traceback

login_bp = Blueprint('login_bp', __name__)
repo = AzureUserRepository()

# ==========================================
# API PÚBLICA (QUITAMOS EL /API MANUAL)
# ==========================================

@login_bp.route('/register', methods=['POST']) # <--- Sin /api
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

@login_bp.route('/forgot-password', methods=['POST']) # <--- Sin /api
def api_forgot_password():
    try:
        data = request.get_json()
        if not data:
            print("[forgot-password] No JSON data received")
            return jsonify({'error': 'No se enviaron datos'}), 400
            
        email = data.get('email')
        print(f"[forgot-password] Solicitud para email: {email}")
        
        if not email:
            return jsonify({'error': 'Email es requerido'}), 400
        
        user = repo.get_user_by_email(email)
        print(f"[forgot-password] Usuario encontrado: {user is not None}")
        
        if not user:
            return jsonify({'error': 'No existe un usuario con ese correo'}), 404

        reset_code = str(random.randint(100000, 999999))
        user_name = getattr(user, 'NAME', email.split('@')[0])
        
        print(f"[forgot-password] Enviando código {reset_code} a {email}")
        
        # Intentar enviar el correo
        result = EmailService.send_password_reset(email, user_name, reset_code)
        
        if result:
            print(f"[forgot-password] Email enviado exitosamente a {email}")
            return jsonify({
                'message': 'Código de recuperación enviado a tu correo',
                'code_for_testing': reset_code  # Solo para testing
            }), 200
        else:
            print(f"[forgot-password] Fallo al enviar email a {email}")
            return jsonify({
                'error': 'Error enviando correo. Verifica tu email.',
                'code_for_testing': reset_code  # Para debugging
            }), 500
            
    except Exception as e:
        print(f"[forgot-password] ERROR: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'error': 'Error procesando solicitud',
            'details': str(e)
        }), 500

@login_bp.route('/reset-password', methods=['POST']) # <--- Sin /api
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

@login_bp.route('/login', methods=['POST'])
def login_api():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = AuthenticationService.authenticate(email, password)

    if user:
        session_data = AuthenticationService.extract_session_data(user, email)
        session.update(session_data)
        return jsonify({
            'message': 'Bienvenido',
            'user': {
                'email': email,
                'role': session.get('user_role'),
                'name': session.get('user_name')
            }
        }), 200
    return jsonify({'error': 'Credenciales incorrectas'}), 401
@login_bp.route('/check_session', methods=['GET']) # <--- Sin /api
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

@login_bp.route('/logout', methods=['POST']) # <--- Sin /api
def logout_api():
    session.clear() 
    return jsonify({'message': 'Sesión cerrada correctamente'}), 200