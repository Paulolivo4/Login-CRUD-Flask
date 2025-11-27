import logging
from datetime import datetime
from typing import Optional, List, Tuple

from BDD.Conexion import get_connection

logger = logging.getLogger(__name__)


class ClientModel:

    @staticmethod
    def create_reservation(
        executor_role: int,
        client_id: int,
        restaurant_id: int,
        reservation_date: datetime,
        number_of_people: int
    ) -> None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "EXEC sp_CrearReserva ?, ?, ?, ?, ?",
                (executor_role, client_id, restaurant_id, reservation_date, number_of_people)
            )
            conn.commit()
            logger.info(f"Reservation created for client {client_id} at restaurant {restaurant_id}")
        except Exception as error:
            logger.error(f"Error creating reservation: {error}")
            raise
        finally:
            conn.close()

    @staticmethod
    def delete_reservation(executor_role: int, reservation_id: int) -> None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "EXEC sp_EliminarReserva ?, ?",
                (executor_role, reservation_id)
            )
            conn.commit()
            logger.info(f"Reservation {reservation_id} deleted successfully")
        except Exception as error:
            logger.error(f"Error deleting reservation {reservation_id}: {error}")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_reservations_by_client(client_id: int) -> List[Tuple]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT ID_RESERVA, ID_CLIENTE, ID_RESTAURANTE, FECHA_RESERVA, "
                "CANTIDAD_PERSONAS, ESTADO FROM RESERVA WHERE ID_CLIENTE = ?",
                (client_id,)
            )
            return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def update_reservation(
        reservation_id: int,
        reservation_date: Optional[datetime] = None,
        number_of_people: Optional[int] = None
    ) -> None:
        if reservation_date is None and number_of_people is None:
            logger.warning(f"No update fields provided for reservation {reservation_id}")
            return

        conn = get_connection()
        try:
            cursor = conn.cursor()

            if reservation_date is not None and number_of_people is not None:
                cursor.execute(
                    "UPDATE RESERVA SET FECHA_RESERVA = ?, CANTIDAD_PERSONAS = ? "
                    "WHERE ID_RESERVA = ?",
                    (reservation_date, number_of_people, reservation_id)
                )
            elif reservation_date is not None:
                cursor.execute(
                    "UPDATE RESERVA SET FECHA_RESERVA = ? WHERE ID_RESERVA = ?",
                    (reservation_date, reservation_id)
                )
            elif number_of_people is not None:
                cursor.execute(
                    "UPDATE RESERVA SET CANTIDAD_PERSONAS = ? WHERE ID_RESERVA = ?",
                    (number_of_people, reservation_id)
                )

            conn.commit()
            logger.info(f"Reservation {reservation_id} updated successfully")

        except Exception as error:
            logger.error(f"Error updating reservation {reservation_id}: {error}")
            raise
        finally:
            conn.close()
