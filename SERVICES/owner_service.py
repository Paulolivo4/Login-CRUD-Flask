import logging
from typing import List, Tuple, Optional, Dict
from MODEL.owner_restaurant import OwnerModel
from MODEL.models import Reserva, Restaurante, Menu
from BDD.db import db

logger = logging.getLogger(__name__)

class OwnerService:

    # --- ESTA ERA LA FUNCIÓN QUE FALTABA Y CAUSABA EL ERROR 500 ---
    @staticmethod
    def get_owner_stats(owner_id: int) -> Dict:
        try:
            # 1. Buscar restaurante del dueño
            restaurant = OwnerModel.get_restaurant_by_owner(owner_id)
            if not restaurant:
                return {'sales': 0, 'reservations': 0, 'rating': 0.0}
            
            restaurant_id = restaurant[0]

            # 2. Contar reservas totales
            total_reservations = Reserva.query.filter_by(ID_RESTAURANTE=restaurant_id).count()

            # 3. Calcular ventas estimadas (Reservas * Precio Promedio $15)
            # Esto evita errores si no hay precios guardados
            total_sales = total_reservations * 15.0 

            return {
                'sales': total_sales,
                'reservations': total_reservations,
                'rating': 5.0 # Valor por defecto seguro
            }
        except Exception as e:
            logger.error(f"Error calculando stats: {e}")
            return {'sales': 0, 'reservations': 0, 'rating': 0}

    @staticmethod
    def get_menus(owner_id: int) -> List[Tuple]:
        try:
            menus = OwnerModel.get_menus_by_owner(owner_id)
            return menus
        except Exception as error:
            logger.error(f"Error retrieving menus for owner {owner_id}: {error}")
            raise

    @staticmethod
    def get_owner_restaurant(owner_id: int) -> Optional[Tuple]:
        try:
            return OwnerModel.get_restaurant_by_owner(owner_id)
        except Exception as error:
            logger.error(f"Error retrieving restaurant for owner {owner_id}: {error}")
            return None

    @staticmethod
    def create_menu(restaurant_id: int, dish_name: str, description: str, price: float, photo_url: Optional[str] = None) -> bool:
        if not restaurant_id or restaurant_id <= 0: raise ValueError("Invalid restaurant ID")
        if not dish_name: raise ValueError("Dish name is required")
        if not price or price <= 0: raise ValueError("Price must be greater than 0")

        try:
            OwnerModel.create_menu(2, restaurant_id, dish_name, description, price, photo_url)
            return True
        except Exception as error:
            logger.error(f"Error creating menu: {error}")
            raise

    @staticmethod
    def delete_menu(menu_id: int) -> bool:
        try:
            OwnerModel.delete_menu(2, menu_id)
            return True
        except Exception as error:
            logger.error(f"Error deleting menu: {error}")
            raise