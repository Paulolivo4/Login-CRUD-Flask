import logging
from sqlalchemy import create_engine
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


def get_connection():
    """Return a SQLAlchemy connection. This keeps compatibility for code
    that previously used `get_connection()`. Prefer using `db.session`
    (Flask-SQLAlchemy) in the application code.
    """
    try:
        from config import get_config

        cfg = get_config()

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

        uri = f"mssql+pyodbc:///?odbc_connect={quote_plus(params)}"
        engine = create_engine(uri)
        connection = engine.connect()
        logger.info("Successfully created SQLAlchemy connection to SQL Server")
        return connection

    except Exception as error:
        logger.error(f"Unexpected connection error: {error}")
        raise