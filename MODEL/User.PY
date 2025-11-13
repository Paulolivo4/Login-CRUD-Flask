from BDD.Conexion import get_connection

class User:

    @staticmethod
    def _row_to_dict(cursor, row):
        if not row:
            return None
        cols = [c[0] for c in cursor.description]
        return {cols[i]: row[i] for i in range(len(cols))}

    @staticmethod
    def obtenerusuarios():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("EXEC sp_GetAllLoginDetails")
        usuarios = cursor.fetchall()
        conn.close()
        return usuarios

    @staticmethod
    def create_new_USER(name, lastname, email, password, rol_id=3):
        """Crea un usuario usando el stored procedure `sp_RegistrarUsuario`.
        Por defecto crea usuarios con rol de cliente (`rol_id=3`).
        """
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("EXEC sp_RegistrarUsuario ?, ?, ?, ?, ?", (name, lastname, email, password, rol_id))
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
        """Intenta autenticar usando `sp_ValidateLogin`.
        Si hay éxito devuelve un diccionario con los datos del usuario (incluyendo ROL_ID),
        en caso contrario devuelve None.
        """
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("EXEC sp_ValidateLogin ?, ?", (email, password))
            row = cursor.fetchone()
            if row:
                user = User._row_to_dict(cursor, row)
                return user

            # Fallback: consulta directa si no existe el SP o no devolvió filas
            cursor.execute("SELECT ID, NAME, LASTNAME, EMAIL, PASSWORD, ROL_ID FROM LOGINDETAILS WHERE EMAIL = ? AND PASSWORD = ?", (email, password))
            row = cursor.fetchone()
            if row:
                user = User._row_to_dict(cursor, row)
                return user
            return None
        finally:
            conn.close()
