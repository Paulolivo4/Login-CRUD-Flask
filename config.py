import os
from typing import Dict
from urllib.parse import quote_plus

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-12345')
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True

class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = 'Lax'

class ProductionConfig(Config):
    # --- CONFIGURACIÓN CRÍTICA PARA RENDER ---
    DEBUG = False
    SESSION_COOKIE_SECURE = True   # Obligatorio para HTTPS
    SESSION_COOKIE_SAMESITE = 'None' # Obligatorio para que el Front acceda al Back
    # -----------------------------------------

    def __init__(self):
        super().__init__()
        self.SECRET_KEY = os.environ.get('SECRET_KEY')

def get_config() -> Config:
    env = os.environ.get('FLASK_ENV', 'production').lower()
    if env == 'production':
        cfg = ProductionConfig()
    else:
        cfg = DevelopmentConfig()

    # Configuración de base de datos Azure
    server = os.environ.get('DB_SERVER')
    database = os.environ.get('DB_NAME')
    username = os.environ.get('DB_USER')
    password = os.environ.get('DB_PASSWORD')
    driver = '{ODBC Driver 18 for SQL Server}'

    params = (
        f"DRIVER={driver};SERVER={server};DATABASE={database};"
        f"UID={username};PWD={password};Encrypt=yes;"
        f"TrustServerCertificate=no;Connection Timeout=30;"
    )
    cfg.SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={quote_plus(params)}"
    return cfg