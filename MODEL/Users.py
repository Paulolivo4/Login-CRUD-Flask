import logging
from typing import Optional, Dict, Any, List

from BDD.Conexion import get_connection

logger = logging.getLogger(__name__)


class User:

    @staticmethod
    def _row_to_dict(cursor, row: tuple) -> Optional[Dict[str, Any]]:
    
        if not row:
            return None

        column_names = [column[0] for column in cursor.description]
        return {column_names[i]: row[i] for i in range(len(column_names))}

    @staticmethod
    def get_all_users() -> List[tuple]:
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("EXEC sp_GetAllLoginDetails")
            return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def create_user(
        name: str,
        lastname: str,
        email: str,
        password: str,
        role_id: int = 3
    ) -> None:
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "EXEC sp_RegistrarUsuario ?, ?, ?, ?, ?",
                (name, lastname, email, password, role_id)
            )
            conn.commit()
            logger.info(f"User created successfully: {email}")
        except Exception as error:
            logger.error(f"Error creating user {email}: {error}")
            raise
        finally:
            conn.close()

    @staticmethod
    def delete_user(email: str) -> None:
       
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("EXEC sp_DeleteLoginDetails ?", (email,))
            conn.commit()
            logger.info(f"User deleted successfully: {email}")
        except Exception as error:
            logger.error(f"Error deleting user {email}: {error}")
            raise
        finally:
            conn.close()

    @staticmethod
    def update_password(email: str, password: str) -> None:
       
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "EXEC sp_UpdateLoginDetails ?, ?",
                (email, password)
            )
            conn.commit()
            logger.info(f"Password updated for user: {email}")
        except Exception as error:
            logger.error(f"Error updating password for {email}: {error}")
            raise
        finally:
            conn.close()

    @staticmethod
    def authenticate(email: str, password: str) -> Optional[Dict[str, Any]]:
        
        conn = get_connection()
        try:
            cursor = conn.cursor()

            # Try stored procedure first
            cursor.execute("EXEC sp_ValidateLogin ?, ?", (email, password))
            row = cursor.fetchone()
            if row:
                user = User._row_to_dict(cursor, row)
                logger.info(f"User authenticated via SP: {email}")
                return user

            # Fallback to direct query
            cursor.execute(
                "SELECT ID, NAME, LASTNAME, EMAIL, PASSWORD, ROL_ID "
                "FROM LOGINDETAILS WHERE EMAIL = ? AND PASSWORD = ?",
                (email, password)
            )
            row = cursor.fetchone()
            if row:
                user = User._row_to_dict(cursor, row)
                logger.info(f"User authenticated via direct query: {email}")
                return user

            logger.warning(f"Authentication failed for user: {email}")
            return None

        except Exception as error:
            logger.error(f"Authentication error for {email}: {error}")
            raise
        finally:
            conn.close()
