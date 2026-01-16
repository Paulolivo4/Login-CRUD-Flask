import logging
import os
from flask_cors import CORS
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for


load_dotenv()

from config import get_config
from CONTROLLER.user_bp import user_bp
from CONTROLLER.login_controller import login_bp
from CONTROLLER.client_controller import client_bp
from CONTROLLER.owner_controller import owner_bp
from CONTROLLER.admin_controller import admin_bp
from BDD.db import init_app as init_db, db
from factories.repository_factory import RepositoryFactory
from SERVICES.user_service import configure_user_repository


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app():
    
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)


    config = get_config()
    app.config.from_object(config)

    # Initialize database (Flask-SQLAlchemy)
    init_db(app)

    # Configurar repositorios / inyección de dependencias (DIP)
    # Por ahora usamos la implementación 'azure' a través de la fábrica.
    user_repo = RepositoryFactory.get_user_repository('azure')
    configure_user_repository(user_repo)

    app.register_blueprint(user_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(client_bp)
    app.register_blueprint(owner_bp)
    app.register_blueprint(admin_bp)

    register_error_handlers(app)

    register_main_routes(app)

    logger.info("Application initialized successfully")
    return app


def register_main_routes(app):
    

    @app.route('/')
    def index():

        return redirect(url_for('login_bp.login'))


def register_error_handlers(app):
    

    @app.errorhandler(403)
    def forbidden(error):
        
        return render_template('VIEW/403.html'), 403

    @app.errorhandler(404)
    def not_found(error):
        
        logger.warning(f"404 error: {error}")
        return render_template('VIEW/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        
        logger.error(f"500 error: {error}")
        return render_template('VIEW/500.html'), 500


if __name__ == '__main__':
    app = create_app()
    config = get_config()
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
