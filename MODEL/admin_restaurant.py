import logging
from typing import List, Tuple
from flask import session

from BDD.db import db
from MODEL.models import Restaurante, LoginDetails, Rol

logger = logging.getLogger(__name__)


class AdminRestaurantModel:
    @staticmethod
    def create_restaurant(
        owner_email: str,
        name: str,
        address: str,
        phone: str
    ) -> None:
        """
        Replica la lógica del stored procedure sp_CrearRestaurante.
        Obtiene el email del admin desde la sesión actual.
        Valida permisos del admin y que el dueño exista y no tenga ya un restaurante.
        """
        # Obtener email del admin autenticado desde la sesión
        admin_email = session.get('user_email')
        if not admin_email:
            raise ValueError("Error: No hay usuario autenticado.")
        
        # 1. Obtener información del administrador por su correo
        admin = LoginDetails.query.filter_by(EMAIL=admin_email).first()
        if not admin:
            raise ValueError(f"Error: No existe un usuario con ese correo de administrador ({admin_email}).")
        
        # 2. Obtener nombre del rol del administrador
        admin_role = Rol.query.get(admin.ROL_ID)
        if not admin_role or admin_role.NOMBRE_ROL != 'Administrador':
            raise PermissionError(f"Permiso denegado: este usuario ({admin_email}) no es administrador.")
        
        # 3. Buscar ID del dueño por correo
        owner = LoginDetails.query.filter_by(EMAIL=owner_email).first()
        if not owner:
            raise ValueError(f"Error: No existe un usuario con ese correo de dueño ({owner_email}).")
        
        # 4. Validar que el dueño no tenga ya un restaurante
        existing_restaurant = Restaurante.query.filter_by(ID_DUENO=owner.ID).first()
        if existing_restaurant:
            raise ValueError(f"Error: Este usuario ({owner_email}) ya tiene un restaurante registrado.")
        
        # 5. Crear restaurante
        restaurante = Restaurante(
            ID_DUENO=owner.ID,
            NOMBRE=name,
            DIRECCION=address,
            TELEFONO=phone,
            ESTADO=True
        )
        db.session.add(restaurante)
        db.session.commit()
        logger.info(f"Restaurant created: {name} for owner {owner_email} by admin {admin_email}")

    @staticmethod
    def get_all_restaurants() -> List[Tuple]:
        results = Restaurante.query.all()
        return [(
            r.ID_RESTAURANTE, r.ID_DUENO, r.NOMBRE, r.DIRECCION, r.TELEFONO, r.ESTADO, r.FECHA_CREACION
        ) for r in results]
    



