import logging
from typing import List, Tuple, Optional, Dict
from datetime import datetime, timedelta

from MODEL.owner_restaurant import OwnerModel
from MODEL.models import Reserva, Restaurante, Menu
from BDD.db import db

logger = logging.getLogger(__name__)


class OwnerService:

    @staticmethod
    def get_menus(owner_id: int) -> List[Tuple]:
        
        try:
            menus = OwnerModel.get_menus_by_owner(owner_id)
            logger.info(f"Retrieved menus for owner {owner_id}")
            return menus
        except Exception as error:
            logger.error(f"Error retrieving menus for owner {owner_id}: {error}")
            raise

    @staticmethod
    def get_owner_restaurant(owner_id: int) -> Optional[Tuple]:
        """Obtiene el restaurante del owner"""
        try:
            restaurant = OwnerModel.get_restaurant_by_owner(owner_id)
            if restaurant:
                logger.info(f"Retrieved restaurant for owner {owner_id}")
            return restaurant
        except Exception as error:
            logger.error(f"Error retrieving restaurant for owner {owner_id}: {error}")
            return None

    @staticmethod
    def create_menu(
        restaurant_id: int,
        dish_name: str,
        description: str,
        price: float,
        photo_url: Optional[str] = None
    ) -> bool:
        
        if not restaurant_id or restaurant_id <= 0:
            raise ValueError("Invalid restaurant ID")

        if not dish_name or len(dish_name.strip()) == 0:
            raise ValueError("Dish name is required")

        if not description or len(description.strip()) == 0:
            raise ValueError("Description is required")

        if not price or price <= 0:
            raise ValueError("Price must be greater than 0")

        try:
            # Role 2 = owner
            OwnerModel.create_menu(2, restaurant_id, dish_name, description, price, photo_url)
            logger.info(f"Menu item created: {dish_name} for restaurant {restaurant_id}")
            return True
        except Exception as error:
            logger.error(f"Error creating menu item {dish_name}: {error}")
            raise

    @staticmethod
    def update_menu(
        menu_id: int,
        dish_name: str,
        description: str,
        price: float,
        photo_url: Optional[str] = None
    ) -> bool:
        
        if not menu_id or menu_id <= 0:
            raise ValueError("Invalid menu ID")

        if not dish_name or len(dish_name.strip()) == 0:
            raise ValueError("Dish name is required")

        if not description or len(description.strip()) == 0:
            raise ValueError("Description is required")

        if not price or price <= 0:
            raise ValueError("Price must be greater than 0")

        try:
            # Role 2 = owner
            OwnerModel.update_menu(2, menu_id, dish_name, description, price, photo_url)
            logger.info(f"Menu item {menu_id} updated successfully")
            return True
        except Exception as error:
            logger.error(f"Error updating menu item {menu_id}: {error}")
            raise

    @staticmethod
    def delete_menu(menu_id: int) -> bool:
        
        if not menu_id or menu_id <= 0:
            raise ValueError("Invalid menu ID")

        try:
            
            OwnerModel.delete_menu(2, menu_id)
            logger.info(f"Menu item {menu_id} deleted successfully")
            return True
        except Exception as error:
            logger.error(f"Error deleting menu item {menu_id}: {error}")
            raise

    @staticmethod
    def create_promotion(
        restaurant_id: int,
        title: str,
        description: str,
        discount: float,
        validity_date: Optional[str] = None
    ) -> bool:
        
        if not restaurant_id or restaurant_id <= 0:
            raise ValueError("Invalid restaurant ID")

        if not title or len(title.strip()) == 0:
            raise ValueError("Title is required")

        if not description or len(description.strip()) == 0:
            raise ValueError("Description is required")

        if not discount or discount <= 0:
            raise ValueError("Discount must be greater than 0")

        try:
            OwnerModel.create_promotion(restaurant_id, title, description, discount, validity_date)
            logger.info(f"Promotion created for restaurant {restaurant_id}: {title}")
            return True
        except Exception as error:
            logger.error(f"Error creating promotion for restaurant {restaurant_id}: {error}")
            raise

    @staticmethod
    def get_owner_stats(owner_id: int) -> Dict:
        """Obtiene estadísticas del restaurante del propietario"""
        try:
            # Obtener el restaurante del owner
            restaurant = OwnerModel.get_restaurant_by_owner(owner_id)
            if not restaurant:
                return {'error': 'No restaurant found for this owner'}
            
            restaurant_id = restaurant[0]  # ID_RESTAURANTE es el primer elemento de la tupla
            
            # Contar reservas totales
            total_reservations = Reserva.query.filter_by(ID_RESTAURANTE=restaurant_id).count()
            
            # Contar reservas del día
            today = datetime.now().date()
            today_start = datetime.combine(today, datetime.min.time())
            today_end = datetime.combine(today, datetime.max.time())
            today_reservations = Reserva.query.filter(
                Reserva.ID_RESTAURANTE == restaurant_id,
                Reserva.FECHA_RESERVA >= today_start,
                Reserva.FECHA_RESERVA <= today_end
            ).count()
            
            # Ingresos totales (aproximado: sumar precios de menús * cantidad personas de reservas)
            # Nota: Se usa cantidad de personas como proxy si no hay tabla de transacciones
            reservations = Reserva.query.filter_by(ID_RESTAURANTE=restaurant_id).all()
            total_revenue = 0.0
            for res in reservations:
                # Obtener menús del restaurante para estimar ingresos
                menus = Menu.query.filter_by(ID_RESTAURANTE=restaurant_id).all()
                if menus:
                    avg_price = sum(m.PRECIO for m in menus) / len(menus)
                    total_revenue += avg_price * res.CANTIDAD_PERSONAS
            
            # Menús disponibles
            available_menus = Menu.query.filter_by(ID_RESTAURANTE=restaurant_id, DISPONIBLE=True).count()
            
            # Datos del restaurante
            resto = Restaurante.query.filter_by(ID_RESTAURANTE=restaurant_id).first()
            
            return {
                'restaurant_id': restaurant_id,
                'restaurant_name': restaurant[1],  # NOMBRE
                'dishes_count': available_menus,  # Renombrar para coincidir con frontend
                'reservations_count': total_reservations,  # Renombrar para coincidir con frontend
                'total_sales': round(total_revenue, 2),  # Renombrar para coincidir con frontend
                'today_reservations': today_reservations,
                'restaurant_address': resto.DIRECCION if resto else 'N/A',
                'restaurant_phone': resto.TELEFONO if hasattr(resto, 'TELEFONO') and resto.TELEFONO else 'N/A'
            }
            
        except Exception as error:
            logger.error(f"Error retrieving owner stats for owner {owner_id}: {error}")
            raise
