import os
import traceback
from flask import Flask, jsonify, request, make_response
from config import get_config
from BDD.db import db, init_app 

from repositories.azure_user_repository import AzureUserRepository 
from SERVICES.user_service import configure_user_repository

def create_app():
    app = Flask(__name__)
    config = get_config()
    app.config.from_object(config)

    # 1. CORS - Configuración Manual (SIN Flask-CORS para evitar conflictos)
    allowed_origins = [
        "https://ufooodfront.onrender.com",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    
    print(f"[CORS] Origins permitidos: {allowed_origins}")

    # Manejo manual de OPTIONS (preflight) - SIEMPRE permitido
    @app.before_request
    def handle_preflight():
        if request.method == 'OPTIONS':
            origin = request.headers.get('Origin', '')
            
            res = make_response()
            # Siempre responder con el origin si está en la lista
            if origin in allowed_origins:
                res.headers['Access-Control-Allow-Origin'] = origin
            else:
                # Por defecto, permitir Render frontend
                res.headers['Access-Control-Allow-Origin'] = 'https://ufooodfront.onrender.com'
            
            res.headers['Access-Control-Allow-Credentials'] = 'true'
            res.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
            res.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            res.headers['Access-Control-Max-Age'] = '3600'
            
            print(f"[CORS] ✓ Preflight OK para origin: {origin}")
            return res, 200
    
    # Asegurar CORS headers en TODAS las respuestas
    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get('Origin', '')
        
        # Agregar headers CORS a TODA respuesta
        if origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
        else:
            response.headers['Access-Control-Allow-Origin'] = 'https://ufooodfront.onrender.com'
        
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        
        return response

    init_app(app)

    # 2. Inyección de Dependencias
    with app.app_context():
        try:
            print("[INIT] Iniciando repositorio de usuarios...")
            user_repo = AzureUserRepository()
            configure_user_repository(user_repo)
            print("[INIT] ✓ Backend conectado a base de datos")
        except Exception as e:
            print(f"[INIT] ⚠️  WARNING BD (no crítico): {e}")
            print(f"[INIT] La app continuará ejecutándose pero sin acceso a BD")
            traceback.print_exc()

    # 3. Registro de Blueprints con Prefijo
    from CONTROLLER.login_controller import login_bp
    from CONTROLLER.user_bp import user_bp
    from CONTROLLER.admin_controller import admin_bp
    from CONTROLLER.owner_controller import owner_bp 
    from CONTROLLER.client_controller import client_bp

    app.register_blueprint(login_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api')
    app.register_blueprint(owner_bp, url_prefix='/api')
    app.register_blueprint(client_bp, url_prefix='/api')

    # Manejadores de errores globales que también respetan CORS
    @app.errorhandler(403)
    def forbidden(error):
        response = jsonify({'error': 'No autorizado para realizar esta acción'})
        response.status_code = 403
        return response

    @app.errorhandler(401)
    def unauthorized(error):
        response = jsonify({'error': 'Por favor inicia sesión para acceder'})
        response.status_code = 401
        return response

    @app.errorhandler(404)
    def not_found(error):
        response = jsonify({'error': 'Ruta no encontrada'})
        response.status_code = 404
        return response

    @app.errorhandler(500)
    def internal_error(error):
        print(f"[ERROR 500] {error}")
        response = jsonify({'error': 'Error interno del servidor', 'details': str(error)})
        response.status_code = 500
        return response

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))