import logging
from datetime import datetime
from typing import Optional, List, Tuple

from BDD.db import db
from MODEL.models import Reserva

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
        reserva = Reserva(
            ID_CLIENTE=client_id,
            ID_RESTAURANTE=restaurant_id,
            FECHA_RESERVA=reservation_date,
            CANTIDAD_PERSONAS=number_of_people,
            ESTADO='CREADA'
        )
        db.session.add(reserva)
        db.session.commit()
        logger.info(f"Reservation created for client {client_id} at restaurant {restaurant_id}")

    @staticmethod
    def delete_reservation(executor_role: int, reservation_id: int) -> None:
        reserva = Reserva.query.get(reservation_id)
        if not reserva:
            raise ValueError("Reservation not found")
        db.session.delete(reserva)
        db.session.commit()
        logger.info(f"Reservation {reservation_id} deleted successfully")

    @staticmethod
    def get_reservations_by_client(client_id: int) -> List[Tuple]:
        # Return reservations with restaurant name for easier display in templates.
        results = db.session.query(Reserva, ).filter(Reserva.ID_CLIENTE == client_id).all()
        # results is list of tuples (Reserva, ) when using query(Reserva)
        # To include restaurant name, perform a join
        joined = db.session.query(Reserva, ).filter(Reserva.ID_CLIENTE == client_id).all()
        # Simpler: fetch Reserva objects and lookup restaurant name per reservation
        reservas = Reserva.query.filter_by(ID_CLIENTE=client_id).all()
        from MODEL.models import Restaurante
        out = []
        for r in reservas:
            nombre_rest = None
            try:
                rest = Restaurante.query.get(r.ID_RESTAURANTE)
                nombre_rest = rest.NOMBRE if rest else str(r.ID_RESTAURANTE)
            except Exception:
                nombre_rest = str(r.ID_RESTAURANTE)

            out.append((
                r.ID_RESERVA, r.ID_CLIENTE, nombre_rest, r.FECHA_RESERVA, r.CANTIDAD_PERSONAS, r.ESTADO
            ))

        return out

    @staticmethod
    def update_reservation(
        reservation_id: int,
        reservation_date: Optional[datetime] = None,
        number_of_people: Optional[int] = None
    ) -> None:
        reserva = Reserva.query.get(reservation_id)
        if not reserva:
            raise ValueError("Reservation not found")
        if reservation_date is not None:
            reserva.FECHA_RESERVA = reservation_date
        if number_of_people is not None:
            reserva.CANTIDAD_PERSONAS = number_of_people
        db.session.commit()
        logger.info(f"Reservation {reservation_id} updated successfully")

