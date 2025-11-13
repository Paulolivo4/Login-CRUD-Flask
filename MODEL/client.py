from BDD.Conexion import get_connection


class ClientModel:
    @staticmethod
    def create_reservation(rol_ejecutor, id_cliente, id_restaurante, fecha, personas):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("EXEC sp_CrearReserva ?, ?, ?, ?, ?", (rol_ejecutor, id_cliente, id_restaurante, fecha, personas))
        conn.commit()
        conn.close()

    @staticmethod
    def delete_reservation(rol_ejecutor, id_reserva):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("EXEC sp_EliminarReserva ?, ?", (rol_ejecutor, id_reserva))
        conn.commit()
        conn.close()

    @staticmethod
    def list_reservations_by_client(id_cliente):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT ID_RESERVA, ID_CLIENTE, ID_RESTAURANTE, FECHA_RESERVA, CANTIDAD_PERSONAS, ESTADO FROM RESERVA WHERE ID_CLIENTE = ?", (id_cliente,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def update_reservation(id_reserva, fecha=None, personas=None):
        # Actualiza fecha y/o cantidad de personas
        conn = get_connection()
        cursor = conn.cursor()
        if fecha is not None and personas is not None:
            cursor.execute("UPDATE RESERVA SET FECHA_RESERVA = ?, CANTIDAD_PERSONAS = ? WHERE ID_RESERVA = ?", (fecha, personas, id_reserva))
        elif fecha is not None:
            cursor.execute("UPDATE RESERVA SET FECHA_RESERVA = ? WHERE ID_RESERVA = ?", (fecha, id_reserva))
        elif personas is not None:
            cursor.execute("UPDATE RESERVA SET CANTIDAD_PERSONAS = ? WHERE ID_RESERVA = ?", (personas, id_reserva))
        else:
            conn.close()
            return
        conn.commit()
        conn.close()
