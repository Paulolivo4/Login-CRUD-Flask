import logging
from typing import List, Tuple, Optional

from MODEL.owner_restaurant import OwnerModel

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
