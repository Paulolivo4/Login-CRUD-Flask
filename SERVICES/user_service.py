import logging
from typing import List, Tuple
from MODEL.Users import User

from UTILS.validators import validate_email, validate_password

logger = logging.getLogger(__name__)


class UserService:

    @staticmethod
    def get_all_users() -> List[Tuple]:
        
        try:
            users = User.get_all_users()
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
        
        if not validate_email(email):
            raise ValueError("Invalid email format")

        if not validate_password(password):
            raise ValueError("Password too short")

        if not name or not lastname:
            raise ValueError("Name and lastname are required")

        try:
            User.create_user(name, lastname, email, password, role_id)
            logger.info(f"User created: {email} with role {role_id}")
            return True
        except Exception as error:
            logger.error(f"Error creating user {email}: {error}")
            raise

    @staticmethod
    def update_password(email: str, password: str) -> bool:
        
        if not validate_email(email):
            raise ValueError("Invalid email format")

        if not validate_password(password):
            raise ValueError("Password too short")

        try:
            User.update_password(email, password)
            logger.info(f"Password updated for user: {email}")
            return True
        except Exception as error:
            logger.error(f"Error updating password for {email}: {error}")
            raise

    @staticmethod
    def delete_user(email: str) -> bool:
        
        if not validate_email(email):
            raise ValueError("Invalid email format")

        try:
            User.delete_user(email)
            logger.info(f"User deleted: {email}")
            return True
        except Exception as error:
            logger.error(f"Error deleting user {email}: {error}")
            raise
