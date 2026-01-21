import os
from typing import Dict
from urllib.parse import quote_plus

class Config:
    # Flask Settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'

    # Server Settings
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5000))

    # Database Configuration
    DB_DRIVER = 'ODBC Driver 18 for SQL Server'
    
    # -------------------------------------------------------------
    # IMPORTANTE: Render debe proveer estas variables de entorno
    # -------------------------------------------------------------
    DB_SERVER = os.environ.get('DB_SERVER')
    DB_NAME = os.environ.get('DB_NAME')
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    
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
    PERMANENT_SESSION_LIFETIME = 3600
    
    # Configuración base de cookies
    SESSION_COOKIE_SECURE = False
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
    SESSION_COOKIE_SAMESITE = 'Lax'


class ProductionConfig(Config):
    DEBUG = False
    # Configuración crítica para que el Frontend (en otro dominio) pueda hacer login
    SESSION_COOKIE_SECURE = True   
    SESSION_COOKIE_SAMESITE = 'None' 

    def __init__(self):
        super().__init__()
        secret_key = os.environ.get('SECRET_KEY')
        # Advertencia en logs si falta la key, pero no rompemos la app aquí
        if not secret_key:
            print("WARNING: SECRET_KEY not set in production environment")
        self.SECRET_KEY = secret_key or 'fallback-secret-key'


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SESSION_COOKIE_SECURE = False


def get_config() -> Config:
    env = os.environ.get('FLASK_ENV', 'development').lower()

    # --- CORRECCIÓN AQUÍ: Asignamos a 'cfg' en lugar de hacer return ---
    if env == 'production':
        cfg = ProductionConfig()
    elif env == 'testing':
        cfg = TestingConfig()
    else:
        cfg = DevelopmentConfig()

    # Validar que tengamos credenciales antes de intentar armar la URI
    # Esto evita errores oscuros si faltan variables en Render
    if not all([cfg.DB_SERVER, cfg.DB_NAME, cfg.DB_USER, cfg.DB_PASSWORD]):
        print("CRITICAL: Faltan variables de entorno de base de datos (DB_SERVER, etc)")

    # Construcción de la URI (Ahora sí se ejecuta siempre)
    params = (
        f"DRIVER={{{cfg.DB_DRIVER}}};"
        f"SERVER={cfg.DB_SERVER};"
        f"DATABASE={cfg.DB_NAME};"
        f"UID={cfg.DB_USER};"
        f"PWD={cfg.DB_PASSWORD};"
        f"Encrypt={'yes' if cfg.DB_ENCRYPT else 'no'};"
        f"TrustServerCertificate={'yes' if cfg.DB_TRUST_CERTIFICATE else 'no'};"
        f"Connection Timeout={cfg.DB_TIMEOUT};"
    )

    cfg.SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={quote_plus(params)}"
    cfg.SQLALCHEMY_TRACK_MODIFICATIONS = False

    return cfg