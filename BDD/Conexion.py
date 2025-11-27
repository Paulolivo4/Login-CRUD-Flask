import logging
import pyodbc

logger = logging.getLogger(__name__)


def get_connection():
    try:
        from config import Config

        connection_string = (
            f"DRIVER={{{Config.DB_DRIVER}}};"
            f"SERVER={Config.DB_SERVER};"
            f"DATABASE={Config.DB_NAME};"
            f"UID={Config.DB_USER};"
            f"PWD={Config.DB_PASSWORD};"
            f"Encrypt={'yes' if Config.DB_ENCRYPT else 'no'};"
            f"TrustServerCertificate={'yes' if Config.DB_TRUST_CERTIFICATE else 'no'};"
            f"Connection Timeout={Config.DB_TIMEOUT};"
        )

        connection = pyodbc.connect(connection_string)
        logger.info("Successfully connected to Azure SQL Server")
        return connection

    except pyodbc.Error as db_error:
        logger.error(f"Database connection error: {db_error}")
        raise
    except Exception as error:
        logger.error(f"Unexpected connection error: {error}")
        raise