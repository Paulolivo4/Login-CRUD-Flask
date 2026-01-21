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
    
    CORS(app, 
     resources={r"/api/*": {
         "origins": [frontend_url, "http://localhost:5173"],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"],
         "supports_credentials": True
     }})

    # Manejo manual de Preflight (Peticiones OPTIONS)
    @app.before_request
    def handle_options_request():
        if request.method == 'OPTIONS':
            res = make_response()
            res.headers['Access-Control-Allow-Origin'] = frontend_url
            res.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            res.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            res.headers['Access-Control-Allow-Credentials'] = 'true'
            return res

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