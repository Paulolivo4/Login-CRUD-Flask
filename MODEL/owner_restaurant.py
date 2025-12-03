import logging
from typing import List, Tuple, Optional

from BDD.db import db
from MODEL.models import Menu, Restaurante, Promocion

logger = logging.getLogger(__name__)


class OwnerModel:

    @staticmethod
    def get_restaurant_by_owner(owner_id: int) -> Optional[Tuple]:
        """Obtiene el restaurante del owner"""
        restaurant = Restaurante.query.filter_by(ID_DUENO=owner_id).first()
        if restaurant:
            return (restaurant.ID_RESTAURANTE, restaurant.NOMBRE, restaurant.ID_DUENO)
        return None

    @staticmethod
    def create_menu(
        executor_role: int,
        restaurant_id: int,
        dish_name: str,
        description: str,
        price: float,
        photo_url: Optional[str] = None
    ) -> None:
        menu = Menu(
            ID_RESTAURANTE=restaurant_id,
            NOMBRE_PLATO=dish_name,
            DESCRIPCION=description,
            PRECIO=price,
            RUTAFOTOMENU=photo_url,
            DISPONIBLE=True
        )
        db.session.add(menu)
        db.session.commit()
        logger.info(f"Menu item created: {dish_name} for restaurant {restaurant_id}")

    @staticmethod
    def update_menu(
        executor_role: int,
        menu_id: int,
        dish_name: str,
        description: str,
        price: float,
        photo_url: Optional[str] = None
    ) -> None:
        menu = Menu.query.get(menu_id)
        if not menu:
            raise ValueError("Menu item not found")
        menu.NOMBRE_PLATO = dish_name
        menu.DESCRIPCION = description
        menu.PRECIO = price
        if photo_url:
            menu.RUTAFOTOMENU = photo_url
        db.session.commit()
        logger.info(f"Menu item {menu_id} updated successfully")

    @staticmethod
    def delete_menu(executor_role: int, menu_id: int) -> None:
        menu = Menu.query.get(menu_id)
        if not menu:
            raise ValueError("Menu item not found")
        db.session.delete(menu)
        db.session.commit()
        logger.info(f"Menu item {menu_id} deleted successfully")

    @staticmethod
    def get_menus_by_owner(owner_id: int) -> List[Tuple]:
        results = (
            db.session.query(Menu)
            .join(Restaurante, Menu.ID_RESTAURANTE == Restaurante.ID_RESTAURANTE)
            .filter(Restaurante.ID_DUENO == owner_id)
            .all()
        )
        return [(
            m.ID_MENU, m.ID_RESTAURANTE, m.NOMBRE_PLATO, m.DESCRIPCION, m.PRECIO, m.DISPONIBLE, m.RUTAFOTOMENU
        ) for m in results]

    @staticmethod
    def create_promotion(
        restaurant_id: int,
        title: str,
        description: str,
        discount: float,
        validity_date: Optional[str] = None
    ) -> None:
        promo = Promocion(
            ID_RESTAURANTE=restaurant_id,
            TITULO=title,
            DESCRIPCION=description,
            DESCUENTO=discount,
            FECHA_VIGENCIA=validity_date
        )
        db.session.add(promo)
        db.session.commit()
        logger.info(f"Promotion created for restaurant {restaurant_id}: {title}")
