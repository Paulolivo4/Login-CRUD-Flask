# Importamos las clases que necesitamos
from repositories.azure_admin_repository import AzureAdminRepository
from repositories.azure_user_repository import AzureUserRepository

class AdminService:
    # Instanciamos los repositorios
    _admin_repo = AzureAdminRepository()
    _user_repo = AzureUserRepository()

    @staticmethod
    def get_all_users():
        """Obtiene todos los usuarios del sistema"""
        try:
            return AdminService._user_repo.get_all_users()
        except Exception as e:
            print(f"Error obteniendo usuarios: {e}")
            raise

    @staticmethod
    def get_all_restaurants():
        return AdminService._admin_repo.get_all_restaurants()

    @staticmethod
    def create_restaurant(owner_id, name, address, phone, opening_time, closing_time, logo_url):
        # Validaciones básicas
        if not all([owner_id, name, address, phone]):
            raise ValueError("Faltan datos requeridos para crear el restaurante")

        # Pasamos los 7 datos al repositorio
        return AdminService._admin_repo.create_restaurant(
            owner_id, name, address, phone, opening_time, closing_time, logo_url
        )

    @staticmethod
    def delete_user(user_id):
        """Elimina un usuario del sistema por ID"""
        try:
            user = AdminService._user_repo.get_user_by_id(user_id)
            if not user:
                return False
            # Usar el email del usuario para borrarlo
            email = user.EMAIL if hasattr(user, 'EMAIL') else user.get('EMAIL')
            return AdminService._user_repo.delete_user(email)
        except Exception as e:
            print(f"Error eliminando usuario: {e}")
            raise

    @staticmethod
    def update_user(user_id, data):
        """Actualiza un usuario del sistema"""
        try:
            # Obtener el usuario actual para validar que existe
            user = AdminService._user_repo.get_user_by_id(user_id)
            if not user:
                return False
            
            # Preparar los datos para actualizar
            name = data.get('name', user.NAME if hasattr(user, 'NAME') else user.get('name'))
            lastname = data.get('lastname', user.LASTNAME if hasattr(user, 'LASTNAME') else user.get('lastname'))
            email = data.get('email', user.EMAIL if hasattr(user, 'EMAIL') else user.get('email'))
            role_id = data.get('role_id', user.ROL_ID if hasattr(user, 'ROL_ID') else user.get('role_id'))
            
            return AdminService._user_repo.update_user(user_id, name, lastname, email, role_id)
        except Exception as e:
            print(f"Error actualizando usuario: {e}")
            raise