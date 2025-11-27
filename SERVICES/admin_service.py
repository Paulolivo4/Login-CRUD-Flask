import logging
from typing import List, Tuple

from MODEL.admin_restaurant import AdminRestaurantModel
from UTILS.validators import validate_email, validate_phone

logger = logging.getLogger(__name__)


class AdminService:

    @staticmethod
    def get_all_restaurants() -> List[Tuple]:
        
        try:
            restaurants = AdminRestaurantModel.get_all_restaurants()
            logger.info("Retrieved all restaurants")
            return restaurants
        except Exception as error:
            logger.error(f"Error retrieving restaurants: {error}")
            raise

    @staticmethod
    def create_restaurant(
        admin_email: str,
        owner_email: str,
        name: str,
        address: str,
        phone: str
    ) -> bool:
        
        if not validate_email(admin_email):
            raise ValueError("Invalid admin email format")

        if not validate_email(owner_email):
            raise ValueError("Invalid owner email format")

        if not name or len(name.strip()) == 0:
            raise ValueError("Restaurant name is required")

        if not address or len(address.strip()) == 0:
            raise ValueError("Address is required")

        if not validate_phone(phone):
            raise ValueError("Invalid phone format")

        try:
            AdminRestaurantModel.create_restaurant(admin_email, owner_email, name, address, phone)
            logger.info(f"Restaurant created: {name} for owner {owner_email}")
            return True
        except Exception as error:
            logger.error(f"Error creating restaurant {name}: {error}")
            raise
