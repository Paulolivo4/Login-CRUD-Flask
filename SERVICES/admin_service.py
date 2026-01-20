# Importamos la clase que acabamos de crear
from repositories.azure_admin_repository import AzureAdminRepository

class AdminService:
    # Instanciamos el repositorio
    _admin_repo = AzureAdminRepository()

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