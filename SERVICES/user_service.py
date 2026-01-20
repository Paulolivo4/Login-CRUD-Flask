from MODEL.Users import Users
from UTILS.validators import validate_email, validate_password
from werkzeug.security import generate_password_hash

class UserService:
    # 1. Definimos la variable de clase explícitamente
    _user_repo = None

    @classmethod
    def configure_repo(cls, repo):
        """Método para inyectar el repositorio"""
        cls._user_repo = repo

    # ==========================================================
    # MÉTODO QUE FALTABA (LOGIN)
    # ==========================================================
    @staticmethod
    def authenticate(email, password):
        if UserService._user_repo is None:
            raise RuntimeError("User repository not configured")
        # Delega la autenticación al repositorio (AzureUserRepository)
        return UserService._user_repo.authenticate(email, password)

    # ==========================================================
    # CRUD Y UTILIDADES
    # ==========================================================
    @staticmethod
    def get_all_users():
        if UserService._user_repo is None:
            print("ADVERTENCIA: Repositorio de usuarios no configurado.")
            return []
        return UserService._user_repo.get_all_users()

    @staticmethod
    def create_user(name, lastname, email, password, role_id):
        if UserService._user_repo is None:
            raise RuntimeError("User repository not configured")
        
        if not validate_email(email):
            raise ValueError("Email inválido")
        
        # Validar contraseña
        if password and not validate_password(password):
            raise ValueError("La contraseña debe tener al menos 8 caracteres, una mayúscula y un número")

        # Nota: Si tu sistema usa hash, úsalo aquí. Si tu BD vieja usa texto plano, 
        # envía password directo. Por defecto en tu repo Azure vi que guardabas hash o texto.
        # Ajusta esto si tus usuarios viejos no entran.
        hashed_password = generate_password_hash(password) if password else None
        
        # Verificar duplicados
        existing_user = UserService._user_repo.get_user_by_email(email)
        if existing_user:
            raise ValueError("El email ya está registrado")

        new_user = Users(None, name, lastname, email, hashed_password, role_id)
        return UserService._user_repo.create_user(new_user)

    @staticmethod
    def delete_user(email):
        if UserService._user_repo is None:
            raise RuntimeError("User repository not configured")
        return UserService._user_repo.delete_user(email)

    @staticmethod
    def update_user_details(user_id, name, lastname, email, role_id):
        if UserService._user_repo is None:
            raise RuntimeError("User repository not configured")
        
        if not name or not email:
            raise ValueError("Nombre y Email son requeridos")
            
        return UserService._user_repo.update_user(user_id, name, lastname, email, role_id)

    @staticmethod
    def update_user_contact_info(user_id, email, phone=None):
        if UserService._user_repo is None:
            raise RuntimeError("User repository not configured")
        
        if not validate_email(email):
            raise ValueError("Email inválido")
            
        return UserService._user_repo.update_user_email(user_id, email)

    @staticmethod
    def get_available_owners():
        """Obtiene usuarios con rol DUEÑO (2) que NO tienen restaurante asignado"""
        if UserService._user_repo is None:
            raise RuntimeError("User repository not configured")
        
        return UserService._user_repo.get_owners_without_restaurant()

# Función helper para usar en app.py
def configure_user_repository(repo):
    UserService.configure_repo(repo)