import logging
from datetime import datetime
from typing import List, Tuple, Optional

from MODEL.client import ClientModel
from UTILS.validators import parse_integer

logger = logging.getLogger(__name__)


class ClientService:

    @staticmethod
    def get_reservations(client_id: int) -> List[Tuple]:
    
        try:
            reservations = ClientModel.get_reservations_by_client(client_id)
            logger.info(f"Retrieved reservations for client {client_id}")
            return reservations
        except Exception as error:
            logger.error(f"Error retrieving reservations for client {client_id}: {error}")
            raise

    @staticmethod
    def create_reservation(
        client_id: int,
        restaurant_id: int,
        reservation_date: datetime,
        number_of_people: int
    ) -> bool:
        
        if not client_id or client_id <= 0:
            raise ValueError("Invalid client ID")

        if not restaurant_id or restaurant_id <= 0:
            raise ValueError("Invalid restaurant ID")

        if not reservation_date:
            raise ValueError("Reservation date is required")

        if not number_of_people or number_of_people <= 0:
            raise ValueError("Number of people must be greater than 0")

        try:
            
            ClientModel.create_reservation(3, client_id, restaurant_id, reservation_date, number_of_people)
            logger.info(f"Reservation created for client {client_id} at restaurant {restaurant_id}")
            return True
        except Exception as error:
            logger.error(f"Error creating reservation: {error}")
            raise

    @staticmethod
    def update_reservation(
        reservation_id: int,
        reservation_date: Optional[datetime] = None,
        number_of_people: Optional[int] = None
    ) -> bool:
        
        if not reservation_id or reservation_id <= 0:
            raise ValueError("Invalid reservation ID")

        if number_of_people is not None and number_of_people <= 0:
            raise ValueError("Number of people must be greater than 0")

        if not reservation_date and not number_of_people:
            raise ValueError("At least one update field must be provided")

        try:
            ClientModel.update_reservation(reservation_id, reservation_date, number_of_people)
            logger.info(f"Reservation {reservation_id} updated successfully")
            return True
        except Exception as error:
            logger.error(f"Error updating reservation {reservation_id}: {error}")
            raise

    @staticmethod
    def delete_reservation(reservation_id: int) -> bool:
        
        if not reservation_id or reservation_id <= 0:
            raise ValueError("Invalid reservation ID")

        try:
            
            ClientModel.delete_reservation(3, reservation_id)
            logger.info(f"Reservation {reservation_id} deleted successfully")
            return True
        except Exception as error:
            logger.error(f"Error deleting reservation {reservation_id}: {error}")
            raise
