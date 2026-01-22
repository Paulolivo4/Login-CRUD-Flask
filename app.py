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

    # 1. Configuración de CORS con Credenciales para Render
    # Nota: No podemos usar "*" si necesitamos credenciales
    allowed_origins = [
        "https://ufooodfront.onrender.com",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    
    print(f"[CORS] Origins permitidos: {allowed_origins}")
    
    CORS(app, 
         origins=allowed_origins,
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         expose_headers=["Content-Type"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
         max_age=3600)

    # Manejo manual de Preflight (Peticiones OPTIONS)
    @app.before_request
    def handle_options_request():
        if request.method == 'OPTIONS':
            origin = request.headers.get('Origin', '')
            res = make_response()
            if origin in allowed_origins:
                res.headers['Access-Control-Allow-Origin'] = origin
                res.headers['Access-Control-Allow-Credentials'] = 'true'
                res.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
                res.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
                res.headers['Access-Control-Max-Age'] = '3600'
            return res, 200
    
    # Agregar headers CORS a todas las respuestas
    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get('Origin', '')
        if origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
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