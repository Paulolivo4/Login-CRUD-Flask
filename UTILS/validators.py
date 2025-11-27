import re
from typing import Optional, Tuple
from datetime import datetime


def validate_email(email: str) -> bool:
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))


def validate_password(password: str, min_length: int = 6) -> bool:
    
    return len(password) >= min_length


def validate_phone(phone: str) -> bool:
    
    phone_pattern = r'^[\d\s\-\+]{7,}$'
    return bool(re.match(phone_pattern, phone))


def parse_role_id(role_input: Optional[str], default_role: int = 3) -> int:
    
    if not role_input:
        return default_role

    try:
        role_id = int(role_input)
        # Validate against known roles (1=admin, 2=owner, 3=client)
        if role_id in (1, 2, 3):
            return role_id
        return default_role
    except (ValueError, TypeError):
        return default_role


def parse_datetime(datetime_str: str) -> Tuple[bool, Optional[datetime]]:
   
    if not datetime_str:
        return False, None

    try:
        # Try ISO format first (YYYY-MM-DDTHH:MM)
        return True, datetime.fromisoformat(datetime_str)
    except (ValueError, TypeError):
        pass

    try:
        # Fallback: replace T with space
        return True, datetime.fromisoformat(datetime_str.replace('T', ' '))
    except (ValueError, TypeError):
        return False, None


def parse_integer(value: Optional[str], default: Optional[int] = None) -> Optional[int]:
    
    if not value:
        return default

    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def parse_float(value: Optional[str], default: Optional[float] = None) -> Optional[float]:
    
    if not value:
        return default

    try:
        return float(value)
    except (ValueError, TypeError):
        return default
