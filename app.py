from flask import Flask, jsonify
from flask_cors import CORS
from config import get_config
from BDD.db import db, init_app 

from repositories.azure_user_repository import AzureUserRepository 
from SERVICES.user_service import configure_user_repository
from CONTROLLER.client_controller import client_bp
def create_app():
    app = Flask(__name__)
    config = get_config()
    app.config.from_object(config)

    # Configurar CORS para conectar con Vue
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)
    
    


    init_app(app)

    # =================================================================
    # INYECCIÓN DE DEPENDENCIAS (CONEXIÓN BD)
    # =================================================================
    with app.app_context():
        try:
            # 1. Crear el repositorio
            user_repo = AzureUserRepository()
            # 2. Conectarlo al servicio
            configure_user_repository(user_repo)
            print("--> Conexión a Base de Datos y Servicios OK.")
        except Exception as e:
            print(f"--> ERROR en configuración BD: {e}")

    # =================================================================
    # REGISTRO DE BLUEPRINTS
    # =================================================================
    from CONTROLLER.login_controller import login_bp
    from CONTROLLER.user_bp import user_bp
    from CONTROLLER.admin_controller import admin_bp
    
    # --- NUEVO: Importar el controlador del Dueño ---
    from CONTROLLER.owner_controller import owner_bp 

    app.register_blueprint(login_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(client_bp)
    # --- NUEVO: Registrar el Blueprint del Dueño ---
    app.register_blueprint(owner_bp)

    # Manejadores de error
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Error interno del servidor', 'details': str(error)}), 500

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Ruta no encontrada'}), 404

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)