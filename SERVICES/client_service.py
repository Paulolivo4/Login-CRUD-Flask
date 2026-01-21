import logging
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any

from MODEL.client import ClientModel
from MODEL.models import Menu, Restaurante
from UTILS.validators import parse_integer
from BDD.db import db

logger = logging.getLogger(__name__)


class ClientService:

    @staticmethod
    def get_all_menus() -> List[Dict[str, Any]]:
        """Obtiene todos los menús disponibles con información del restaurante."""
        try:
            menus = db.session.query(Menu, Restaurante).join(
                Restaurante, Menu.ID_RESTAURANTE == Restaurante.ID_RESTAURANTE
            ).filter(Menu.DISPONIBLE == True, Restaurante.ESTADO == True).all()
            
            result = []
            for menu, restaurante in menus:
                result.append({
                    'ID_MENU': menu.ID_MENU,
                    'ID_RESTAURANTE': restaurante.ID_RESTAURANTE,
                    'NOMBRE_PLATO': menu.NOMBRE_PLATO,
                    'DESCRIPCION': menu.DESCRIPCION,
                    'PRECIO': menu.PRECIO,
                    'RUTAFOTOMENU': menu.RUTAFOTOMENU,
                    'NOMBRE_RESTAURANTE': restaurante.NOMBRE,
                    'DIRECCION': restaurante.DIRECCION,
                    'TELEFONO': restaurante.TELEFONO,
                    'RUTAFOTOLOGO': getattr(restaurante, 'RUTAFOTOLOGO', None),
                })
            
            logger.info(f"Retrieved {len(result)} available menus")
            return result
        except Exception as error:
            logger.error(f"Error retrieving menus: {error}")
            raise

    @staticmethod
    def get_menu_detail(menu_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene detalle de un menú específico."""
        try:
            menu = Menu.query.get(menu_id)
            if not menu:
                return None
            
            restaurante = Restaurante.query.get(menu.ID_RESTAURANTE)
            
            return {
                'ID_MENU': menu.ID_MENU,
                'ID_RESTAURANTE': restaurante.ID_RESTAURANTE,
                'NOMBRE_PLATO': menu.NOMBRE_PLATO,
                'DESCRIPCION': menu.DESCRIPCION,
                'PRECIO': menu.PRECIO,
                'RUTAFOTOMENU': menu.RUTAFOTOMENU,
                'NOMBRE_RESTAURANTE': restaurante.NOMBRE,
                'DIRECCION': restaurante.DIRECCION,
                'TELEFONO': restaurante.TELEFONO,
                'RUTAFOTOLOGO': getattr(restaurante, 'RUTAFOTOLOGO', None),
            }
        except Exception as error:
            logger.error(f"Error retrieving menu detail: {error}")
            raise

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
    def get_available_restaurants() -> List[dict]:
        """Return a list of active restaurants as dicts with id and name."""
        try:
            restos = Restaurante.query.filter_by(ESTADO=True).all()
            result = []
            for r in restos:
                result.append({'ID_RESTAURANTE': r.ID_RESTAURANTE, 'NOMBRE': r.NOMBRE})
            logger.info(f"Retrieved {len(result)} active restaurants")
            return result
        except Exception as error:
            logger.error(f"Error retrieving restaurants: {error}")
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
    @staticmethod
    def get_all_restaurants() -> List[Restaurante]:
        """Obtiene la lista completa de objetos Restaurante activos."""
        try:
            # Traemos el objeto completo para tener acceso a todos sus campos
            restos = Restaurante.query.filter_by(ESTADO=True).all()
            logger.info(f"Retrieved {len(restos)} active restaurants")
            return restos
        except Exception as error:
            logger.error(f"Error retrieving restaurants: {error}")
            raise