import logging
from typing import List, Tuple, Optional, Dict, Any

from UTILS.validators import validate_email, validate_password
from repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

# Variable de módulo que contendrá el repositorio concreto inyectado en tiempo de arranque
_user_repo: Optional[UserRepository] = None


def configure_user_repository(repo: UserRepository) -> None:
    """Configura el repositorio de usuarios (inyección de dependencia).
    Debe llamarse desde `app.create_app()` antes de registrar blueprints.
    """
    global _user_repo
    _user_repo = repo


class UserService:
    """Service que actúa como fachada para operaciones de usuario.
    Sigue exponiendo la API previa para no romper controladores, pero
    delega la lógica de acceso a datos a un `UserRepository` (DIP).
    """

    @staticmethod
    def get_all_users() -> List[Dict[str, Any]]:
        if _user_repo is None:
            raise RuntimeError("User repository not configured")
        try:
            users = _user_repo.get_all()
            logger.info("Retrieved all users")
            return users
        except Exception as error:
            logger.error(f"Error retrieving users: {error}")
            raise

    @staticmethod
    def create_user(
        name: str,
        lastname: str,
        email: str,
        password: str,
        role_id: int = 3
    ) -> bool:
        if _user_repo is None:
            raise RuntimeError("User repository not configured")

        if not validate_email(email):
            raise ValueError("Invalid email format")

        if not validate_password(password):
            raise ValueError("Password too short")

        if not name or not lastname:
            raise ValueError("Name and lastname are required")

        try:
            _user_repo.create(name, lastname, email, password, role_id)
            logger.info(f"User created: {email} with role {role_id}")
            return True
        except Exception as error:
            logger.error(f"Error creating user {email}: {error}")
            raise

    @staticmethod
    def update_password(email: str, password: str) -> bool:
        if _user_repo is None:
            raise RuntimeError("User repository not configured")

        if not validate_email(email):
            raise ValueError("Invalid email format")

        if not validate_password(password):
            raise ValueError("Password too short")

        try:
            _user_repo.update_password(email, password)
            logger.info(f"Password updated for user: {email}")
            return True
        except Exception as error:
            logger.error(f"Error updating password for {email}: {error}")
            raise

    @staticmethod
    def delete_user(email: str) -> bool:
        if _user_repo is None:
            raise RuntimeError("User repository not configured")

        if not validate_email(email):
            raise ValueError("Invalid email format")

        try:
            _user_repo.delete(email)
            logger.info(f"User deleted: {email}")
            return True
        except Exception as error:
            logger.error(f"Error deleting user {email}: {error}")
            raise

    @staticmethod
    def authenticate(email: str, password: str) -> Optional[Dict[str, Any]]:
        if _user_repo is None:
            raise RuntimeError("User repository not configured")
        try:
            return _user_repo.authenticate(email, password)
        except Exception as error:
            logger.error(f"Authentication error for {email}: {error}")
            return None
