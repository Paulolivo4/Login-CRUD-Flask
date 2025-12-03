import logging
from typing import Optional, Dict, Any, List

from BDD.db import db
from MODEL.models import LoginDetails

logger = logging.getLogger(__name__)


class User:

    @staticmethod
    def get_all_users() -> List[Dict[str, Any]]:
        users = LoginDetails.query.all()
        return [u.to_dict() for u in users]

    @staticmethod
    def create_user(
        name: str,
        lastname: str,
        email: str,
        password: str,
        role_id: int = 3
    ) -> None:
        user = LoginDetails(
            NAME=name,
            LASTNAME=lastname,
            EMAIL=email,
            PASSWORD=password,
            ROL_ID=role_id
        )
        db.session.add(user)
        db.session.commit()
        logger.info(f"User created successfully: {email}")

    @staticmethod
    def delete_user(email: str) -> None:
        user = LoginDetails.query.filter_by(EMAIL=email).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            logger.info(f"User deleted successfully: {email}")
        else:
            logger.warning(f"User to delete not found: {email}")

    @staticmethod
    def update_password(email: str, password: str) -> None:
        user = LoginDetails.query.filter_by(EMAIL=email).first()
        if not user:
            raise ValueError("Usuario no encontrado")
        user.PASSWORD = password
        db.session.commit()
        logger.info(f"Password updated for user: {email}")

    @staticmethod
    def authenticate(email: str, password: str) -> Optional[Dict[str, Any]]:
        user = LoginDetails.query.filter_by(EMAIL=email, PASSWORD=password).first()
        if user:
            logger.info(f"User authenticated: {email}")
            return user.to_dict()
        logger.warning(f"Authentication failed for user: {email}")
        return None
