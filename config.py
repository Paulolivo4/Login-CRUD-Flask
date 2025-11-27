import os
from typing import Dict


class Config:

    # Flask Settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'

    # Server Settings
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5000))

    # Database Configuration
    DB_DRIVER = 'ODBC Driver 18 for SQL Server'
    DB_SERVER = os.environ.get(
        'DB_SERVER',
        'ufoodsql.database.windows.net'
    )
    DB_NAME = os.environ.get('DB_NAME', 'UFOOD')
    DB_USER = os.environ.get('DB_USER', 'adminsql')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'Chispo11')
    DB_ENCRYPT = True
    DB_TRUST_CERTIFICATE = False
    DB_TIMEOUT = 30

    # Role IDs
    ROLE_ADMIN = 1
    ROLE_OWNER = 2
    ROLE_CLIENT = 3

    # Role Mapping
    ROLES: Dict[int, str] = {
        ROLE_ADMIN: 'admin',
        ROLE_OWNER: 'owner',
        ROLE_CLIENT: 'client',
    }

    # Session Configuration
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour in seconds
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Error Messages
    ERROR_MESSAGES = {
        'invalid_credentials': 'Credenciales inválidas',
        'user_not_found': 'Usuario no encontrado',
        'registration_error': 'Error al registrar usuario',
        'invalid_data': 'Datos inválidos',
        'unauthorized': 'No autorizado para realizar esta acción',
        'database_error': 'Error de base de datos',
    }

    # Success Messages
    SUCCESS_MESSAGES = {
        'login_success': 'Has iniciado sesión correctamente',
        'logout_success': 'Has cerrado sesión',
        'registration_success': 'Usuario registrado correctamente',
        'password_updated': 'Contraseña actualizada correctamente',
        'user_created': 'Usuario creado correctamente',
        'user_updated': 'Usuario actualizado correctamente',
        'user_deleted': 'Usuario eliminado correctamente',
        'reservation_created': 'Reserva creada correctamente',
        'reservation_updated': 'Reserva actualizada correctamente',
        'reservation_deleted': 'Reserva eliminada correctamente',
        'menu_created': 'Menú creado correctamente',
        'menu_updated': 'Menú actualizado correctamente',
        'menu_deleted': 'Menú eliminado correctamente',
        'restaurant_created': 'Restaurante creado correctamente',
    }


class DevelopmentConfig(Config):
    
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):

    DEBUG = False

    def __init__(self):
        super().__init__()
        secret_key = os.environ.get('SECRET_KEY')
        if not secret_key:
            raise ValueError('SECRET_KEY environment variable must be set in production')
        self.SECRET_KEY = secret_key


class TestingConfig(Config):

    TESTING = True
    DEBUG = True
    SESSION_COOKIE_SECURE = False


def get_config() -> Config:
    env = os.environ.get('FLASK_ENV', 'development').lower()

    if env == 'production':
        return ProductionConfig()
    elif env == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()
