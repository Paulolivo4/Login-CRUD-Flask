import logging
from typing import List, Tuple, Optional

from BDD.Conexion import get_connection

logger = logging.getLogger(__name__)


class OwnerModel:

    @staticmethod
    def create_menu(
        executor_role: int,
        restaurant_id: int,
        dish_name: str,
        description: str,
        price: float
    ) -> None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "EXEC sp_CrearMenu ?, ?, ?, ?, ?",
                (executor_role, restaurant_id, dish_name, description, price)
            )
            conn.commit()
            logger.info(f"Menu item created: {dish_name} for restaurant {restaurant_id}")
        except Exception as error:
            logger.error(f"Error creating menu item {dish_name}: {error}")
            raise
        finally:
            conn.close()

    @staticmethod
    def update_menu(
        executor_role: int,
        menu_id: int,
        dish_name: str,
        description: str,
        price: float
    ) -> None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "EXEC sp_EditarMenu ?, ?, ?, ?, ?",
                (executor_role, menu_id, dish_name, description, price)
            )
            conn.commit()
            logger.info(f"Menu item {menu_id} updated successfully")
        except Exception as error:
            logger.error(f"Error updating menu item {menu_id}: {error}")
            raise
        finally:
            conn.close()

    @staticmethod
    def delete_menu(executor_role: int, menu_id: int) -> None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "EXEC sp_EliminarMenu ?, ?",
                (executor_role, menu_id)
            )
            conn.commit()
            logger.info(f"Menu item {menu_id} deleted successfully")
        except Exception as error:
            logger.error(f"Error deleting menu item {menu_id}: {error}")
            raise
        finally:
            conn.close()

    @staticmethod
    def get_menus_by_owner(owner_id: int) -> List[Tuple]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT m.ID_MENU, m.ID_RESTAURANTE, m.NOMBRE_PLATO, "
                "m.DESCRIPCION, m.PRECIO, m.DISPONIBLE "
                "FROM MENU m "
                "JOIN RESTAURANTE r ON m.ID_RESTAURANTE = r.ID_RESTAURANTE "
                "WHERE r.ID_DUENO = ?",
                (owner_id,)
            )
            return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def create_promotion(
        restaurant_id: int,
        title: str,
        description: str,
        discount: float,
        validity_date: Optional[str] = None
    ) -> None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO PROMOCIONES "
                "(ID_RESTAURANTE, TITULO, DESCRIPCION, DESCUENTO, FECHA_VIGENCIA) "
                "VALUES (?, ?, ?, ?, ?)",
                (restaurant_id, title, description, discount, validity_date)
            )
            conn.commit()
            logger.info(f"Promotion created for restaurant {restaurant_id}: {title}")
        except Exception as error:
            logger.error(f"Error creating promotion for restaurant {restaurant_id}: {error}")
            raise
        finally:
            conn.close()
