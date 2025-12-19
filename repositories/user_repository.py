from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class UserRepository(ABC):
    """Abstracción del repositorio de usuarios. Controladores y servicios
    dependerán de esta interfaz (DIP)."""

    @abstractmethod
    def get_all(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def create(self, name: str, lastname: str, email: str, password: str, role_id: int = 3) -> None:
        pass

    @abstractmethod
    def delete(self, email: str) -> None:
        pass

    @abstractmethod
    def update_password(self, email: str, password: str) -> None:
        pass

    @abstractmethod
    def authenticate(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        pass
