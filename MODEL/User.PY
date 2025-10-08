from BDD.Conexion import get_connection

class User:

    @staticmethod
    def obtenerusuarios():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("EXEC sp_GetAllLoginDetails")
        usuarios = cursor.fetchall()
        conn.close()
        return usuarios

    @staticmethod
    def create_new_USER(name, lastname ,email, password):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("EXEC sp_InsertLoginDetails ?, ?, ?, ?", (name, lastname ,email, password))
        conn.commit()
        conn.close()

    @staticmethod
    def delete_user(email):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("EXEC sp_DeleteLoginDetails ?", (email,))
        conn.commit()
        conn.close()

    @staticmethod
    def update_user(email, password):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("EXEC sp_UpdateLoginDetails ?, ?", (email, password))
        conn.commit()
        conn.close()

    @staticmethod
    def authenticate(email, password):
        """Devuelve True si las credenciales son válidas, False en caso contrario."""
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Intentar usar un stored procedure si existe
            cursor.execute("EXEC sp_ValidateLogin ?, ?", (email, password))
            row = cursor.fetchone()
            if row:
                return True
            # Si no hay SP, intentar consulta directa (seguro en entorno controlado)
            cursor.execute("SELECT password FROM LOGINDETAILS WHERE email = ?", (email,))
            r = cursor.fetchone()
            if r and r[0] == password:
                return True
            return False
        except Exception:
            
            # En caso de error, no autenticar
            return False
        finally:
            conn.close()
