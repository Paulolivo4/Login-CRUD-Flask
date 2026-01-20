from abc import ABC, abstractmethod

class UserRepository(ABC):
    """
    Interfaz (Contrato) que define qué métodos DEBE tener cualquier 
    repositorio de usuarios para que el sistema funcione.
    """

    @abstractmethod
    def get_all_users(self):
        """Obtiene todos los usuarios"""
        pass

    @abstractmethod
    def create_user(self, user_entity):
        """Crea un nuevo usuario"""
        pass

    @abstractmethod
    def delete_user(self, email):
        """Elimina un usuario por email"""
        pass

    @abstractmethod
    def get_user_by_email(self, email):
        """Busca un usuario por email"""
        pass
    
    @abstractmethod
    def authenticate(self, email, password):
        """Verifica credenciales"""
        pass

    @abstractmethod
    def update_user(self, user_id, name, lastname, email, role_id):
        """Actualiza datos del usuario"""
        pass
    
    # Métodos opcionales (pueden no ser abstractos si no quieres obligar a todos)
    def update_password(self, email, password):
        pass
        
    def get_owners_without_restaurant(self):
        pass

    def update_user_email(self, user_id, email):
        pass