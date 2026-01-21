import os
from typing import Dict
from urllib.parse import quote_plus

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5000))

    # Database
    DB_DRIVER = 'ODBC Driver 18 for SQL Server'
    DB_SERVER = os.environ.get('DB_SERVER', 'ufoodsql.database.windows.net')
    DB_NAME = os.environ.get('DB_NAME', 'UFOOD')
    DB_USER = os.environ.get('DB_USER', 'adminsql')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'Chispo11')
    DB_ENCRYPT = True
    DB_TRUST_CERTIFICATE = False 
    DB_TIMEOUT = 30

    # Roles
    ROLE_ADMIN = 1
    ROLE_OWNER = 2
    ROLE_CLIENT = 3
    ROLES: Dict[int, str] = {
        ROLE_ADMIN: 'admin',
        ROLE_OWNER: 'owner',
        ROLE_CLIENT: 'client',
    }

    # Sesión Base
    PERMANENT_SESSION_LIFETIME = 3600
    SESSION_COOKIE_HTTPONLY = True
    
    # MENSAJES DE ERROR/EXITO (Mantenemos los tuyos)
    ERROR_MESSAGES = { 'invalid_credentials': 'Credenciales inválidas', 'user_not_found': 'Usuario no encontrado', 'registration_error': 'Error al registrar usuario', 'invalid_data': 'Datos inválidos', 'unauthorized': 'No autorizado', 'database_error': 'Error de base de datos' }
    SUCCESS_MESSAGES = { 'login_success': 'Has iniciado sesión correctamente', 'logout_success': 'Has cerrado sesión', 'registration_success': 'Usuario registrado correctamente', 'password_updated': 'Contraseña actualizada correctamente', 'user_created': 'Usuario creado', 'user_updated': 'Usuario actualizado', 'user_deleted': 'Usuario eliminado', 'reservation_created': 'Reserva creada', 'reservation_updated': 'Reserva actualizada', 'reservation_deleted': 'Reserva eliminada', 'menu_created': 'Menú creado', 'menu_updated': 'Menú actualizado', 'menu_deleted': 'Menú eliminado', 'restaurant_created': 'Restaurante creado' }


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = 'Lax' # En local Lax está bien

class ProductionConfig(Config):
    DEBUG = False
    
    # --- CORRECCIÓN CRÍTICA PARA RENDER ---
    SESSION_COOKIE_SECURE = True   
    SESSION_COOKIE_SAMESITE = 'None' # Obligatorio para cross-site (Front vs Back)
    # --------------------------------------

    def __init__(self):
        super().__init__()
        secret_key = os.environ.get('SECRET_KEY')
        if not secret_key:
             # Evitamos romper la app si falta, pero avisamos
            print("WARNING: SECRET_KEY not set")
        self.SECRET_KEY = secret_key or 'fallback_secret'

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SESSION_COOKIE_SECURE = False

def get_config() -> Config:
    env = os.environ.get('FLASK_ENV', 'development').lower()

    if env == 'production':
        cfg = ProductionConfig()
    elif env == 'testing':
        cfg = TestingConfig()
    else:
        cfg = DevelopmentConfig()

    params = (
        f"DRIVER={{{cfg.DB_DRIVER}}};SERVER={cfg.DB_SERVER};DATABASE={cfg.DB_NAME};"
        f"UID={cfg.DB_USER};PWD={cfg.DB_PASSWORD};Encrypt={'yes' if cfg.DB_ENCRYPT else 'no'};"
        f"TrustServerCertificate={'yes' if cfg.DB_TRUST_CERTIFICATE else 'no'};Connection Timeout={cfg.DB_TIMEOUT};"
    )
    cfg.SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={quote_plus(params)}"
    cfg.SQLALCHEMY_TRACK_MODIFICATIONS = False
    return cfg