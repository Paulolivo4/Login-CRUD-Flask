import logging
from typing import Optional, Dict, Any

from MODEL.Users import User
from config import Config

logger = logging.getLogger(__name__)


class AuthenticationService:

    @staticmethod
    def authenticate(email: str, password: str) -> Optional[Dict[str, Any]]:
        
        try:
            user = User.authenticate(email, password)
            if user:
                logger.info(f"User authenticated: {email}")
            else:
                logger.warning(f"Authentication failed for: {email}")
            return user
        except Exception as error:
            logger.error(f"Authentication service error for {email}: {error}")
            return None

    @staticmethod
    def extract_session_data(user: Dict[str, Any], email: str) -> Dict[str, Any]:
        
        def get_field_value(user_dict, *keys):
            
            for key in keys:
                if isinstance(user_dict, dict) and key in user_dict and user_dict[key] is not None:
                    return user_dict[key]
            return None

        return {
            'user_email': get_field_value(user, 'EMAIL', 'Email', 'email') or email,
            'user_id': get_field_value(user, 'ID', 'Id', 'id'),
            'user_role': get_field_value(user, 'ROL_ID', 'ROL', 'Rol', 'rol_id', 'rol'),
            'user_name': get_field_value(user, 'NAME', 'Name', 'name'),
        }

    @staticmethod
    def get_role_name(role_id: Any) -> str:
        
        try:
            role_id = int(role_id) if isinstance(role_id, str) else role_id
            return Config.ROLES.get(role_id, 'unknown')
        except (ValueError, TypeError):
            return 'unknown'

    @staticmethod
    def is_admin(role_id: Any) -> bool:
        
        try:
            return int(role_id) == Config.ROLE_ADMIN
        except (ValueError, TypeError):
            return False

    @staticmethod
    def is_owner(role_id: Any) -> bool:
        
        try:
            return int(role_id) == Config.ROLE_OWNER
        except (ValueError, TypeError):
            return False

    @staticmethod
    def is_client(role_id: Any) -> bool:
        
        try:
            return int(role_id) == Config.ROLE_CLIENT
        except (ValueError, TypeError):
            return False
