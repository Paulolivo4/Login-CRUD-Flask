import os
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from config import get_config
from BDD.db import db, init_app 

from repositories.azure_user_repository import AzureUserRepository 
from SERVICES.user_service import configure_user_repository

def create_app():
    app = Flask(__name__)
    config = get_config()
    app.config.from_object(config)

    # 1. Configuración de CORS Blindada
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173').rstrip('/')
    allowed_origins = [
        frontend_url,
        "http://localhost:5173",
        "http://localhost:3000",
        "https://ufooodfront.onrender.com",  # URL del frontend en Render
    ]
    print(f"[CORS] Frontend URL permitida: {frontend_url}")
    print(f"[CORS] Origins permitidos: {allowed_origins}")
    
    # Habilitar CORS para todas las rutas
    CORS(app, 
         resources={r"/*": {
             "origins": allowed_origins,
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
             "allow_headers": ["Content-Type", "Authorization"],
             "expose_headers": ["Content-Type"],
             "supports_credentials": True,
             "max_age": 3600
         }})

    # Manejo manual de Preflight (Peticiones OPTIONS) y headers en todas las respuestas
    @app.before_request
    def handle_options_request():
        if request.method == 'OPTIONS':
            origin = request.headers.get('Origin', frontend_url)
            res = make_response()
            res.headers['Access-Control-Allow-Origin'] = origin if origin in allowed_origins else frontend_url
            res.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
            res.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            res.headers['Access-Control-Allow-Credentials'] = 'true'
            res.headers['Access-Control-Max-Age'] = '3600'
            return res
    
    # Agregar headers CORS a todas las respuestas
    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get('Origin', frontend_url)
        response.headers['Access-Control-Allow-Origin'] = origin if origin in allowed_origins else frontend_url
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response

    init_app(app)

    # 2. Inyección de Dependencias
    with app.app_context():
        try:
            user_repo = AzureUserRepository()
            configure_user_repository(user_repo)
            print(f"--> Backend conectado: {frontend_url}")
        except Exception as e:
            print(f"--> ERROR BD: {e}")

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

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Ruta no encontrada'}), 404

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))