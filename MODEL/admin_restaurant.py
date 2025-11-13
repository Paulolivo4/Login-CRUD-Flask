from BDD.Conexion import get_connection


class AdminRestaurantModel:
    @staticmethod
    def create_restaurant(email_admin, email_dueno, nombre, direccion, telefono):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("EXEC sp_CrearRestaurante ?, ?, ?, ?, ?", (email_admin, email_dueno, nombre, direccion, telefono))
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def list_restaurants():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID_RESTAURANTE, ID_DUENO, NOMBRE, DIRECCION, TELEFONO, ESTADO, FECHA_CREACION FROM RESTAURANTE")
        rows = cursor.fetchall()
        conn.close()
        return rows
