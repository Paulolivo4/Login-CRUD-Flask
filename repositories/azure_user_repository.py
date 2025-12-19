import logging
from typing import List, Dict, Any, Optional

from BDD.db import db
from MODEL.models import LoginDetails
from repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class AzureUserRepository(UserRepository):
    """Implementación concreta del repositorio usando SQLAlchemy
    (aquí llamado 'Azure' por la especificación del ejercicio)."""

    def get_all(self) -> List[Dict[str, Any]]:
        users = LoginDetails.query.all()
        return [u.to_dict() for u in users]

    def create(self, name: str, lastname: str, email: str, password: str, role_id: int = 3) -> None:
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

    def delete(self, email: str) -> None:
        user = LoginDetails.query.filter_by(EMAIL=email).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            logger.info(f"User deleted successfully: {email}")
        else:
            logger.warning(f"User to delete not found: {email}")

    def update_password(self, email: str, password: str) -> None:
        user = LoginDetails.query.filter_by(EMAIL=email).first()
        if not user:
            raise ValueError("Usuario no encontrado")
        user.PASSWORD = password
        db.session.commit()
        logger.info(f"Password updated for user: {email}")

    def authenticate(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        user = LoginDetails.query.filter_by(EMAIL=email, PASSWORD=password).first()
        if user:
            logger.info(f"User authenticated: {email}")
            return user.to_dict()
        logger.warning(f"Authentication failed for user: {email}")
        return None
