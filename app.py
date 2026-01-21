import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import get_config
from BDD.db import db, init_app 

from repositories.azure_user_repository import AzureUserRepository 
from SERVICES.user_service import configure_user_repository
from CONTROLLER.client_controller import client_bp
from CONTROLLER.login_controller import login_bp
from CONTROLLER.user_bp import user_bp
from CONTROLLER.admin_controller import admin_bp
from CONTROLLER.owner_controller import owner_bp 

def create_app():
    app = Flask(__name__)
    config = get_config()
    app.config.from_object(config)

    # =================================================================
    # CONFIGURACIÓN CORS PARA PRODUCCIÓN
    # =================================================================
    # En local usa localhost, en Render usa la variable de entorno FRONTEND_URL
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
    
    # Importante: Para cookies/sesiones entre dominios diferentes (API vs Front)
    # se requiere supports_credentials=True
    CORS(app, resources={r"/api/*": {"origins": frontend_url}}, supports_credentials=True)

    # Configuración adicional de cookies para producción (Render usa HTTPS)
    if os.environ.get('FLASK_ENV') == 'production':
        app.config.update(
            SESSION_COOKIE_SECURE=True,
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SAMESITE='None' # Necesario si Front y Back están en dominios distintos
        )

    init_app(app)

    # =================================================================
    # INYECCIÓN DE DEPENDENCIAS
    # =================================================================
    # Patrón: Composition Root (Configuramos el grafo de objetos aquí)
    with app.app_context():
        try:
            user_repo = AzureUserRepository()
            configure_user_repository(user_repo)
            print("--> Conexión a Base de Datos y Servicios OK.")
        except Exception as e:
            print(f"--> ERROR en configuración BD: {e}")

    # =================================================================
    # REGISTRO DE BLUEPRINTS
    # =================================================================
    app.register_blueprint(login_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(owner_bp)

    # Manejadores de error globales (Formato JSON consistente)
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Error interno del servidor', 'details': str(error)}), 500

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Ruta no encontrada'}), 404

    return app

if __name__ == '__main__':
    app = create_app()
    # En local debug=True, en producción lo maneja Gunicorn
    app.run(host='0.0.0.0', port=5000, debug=True)