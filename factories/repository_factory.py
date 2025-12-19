from typing import Optional

from repositories.azure_user_repository import AzureUserRepository
from repositories.user_repository import UserRepository


class RepositoryFactory:
    """Factory simple para crear repositorios concretos.
    Permite extender sin modificar controladores (OCP).
    """

    @staticmethod
    def get_user_repository(repo_type: str = 'azure') -> UserRepository:
        if repo_type == 'azure':
            return AzureUserRepository()
        raise ValueError(f'Unsupported repository type: {repo_type}')
