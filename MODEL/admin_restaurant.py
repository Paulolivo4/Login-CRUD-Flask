import logging
from typing import List, Tuple

from BDD.Conexion import get_connection

logger = logging.getLogger(__name__)


class AdminRestaurantModel:
    @staticmethod
    def create_restaurant(
        admin_email: str,
        owner_email: str,
        name: str,
        address: str,
        phone: str
    ) -> None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "EXEC sp_CrearRestaurante ?, ?, ?, ?, ?",
                (admin_email, owner_email, name, address, phone)
            )
            conn.commit()
            logger.info(f"Restaurant created: {name} for owner {owner_email}")
        except Exception as error:
            logger.error(f"Error creating restaurant {name}: {error}")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_all_restaurants() -> List[Tuple]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT ID_RESTAURANTE, ID_DUENO, NOMBRE, DIRECCION, TELEFONO, "
                "ESTADO, FECHA_CREACION FROM RESTAURANTE"
            )
            return cursor.fetchall()
        finally:
            conn.close()
