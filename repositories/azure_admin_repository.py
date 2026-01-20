from BDD.db import db
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

class AzureAdminRepository:
    
    def get_all_restaurants(self):
        """Obtiene la lista de restaurantes para mostrar en la tabla"""
        try:
            # Asegúrate que el nombre de la tabla es RESTAURANTE (singular)
            sql = text("SELECT * FROM RESTAURANTE")
            result = db.session.execute(sql)
            return result.fetchall()
        except Exception as e:
            logger.error(f"Error getting restaurants: {e}")
            return []

    def create_restaurant(self, owner_id, name, address,   phone, opening_time, closing_time, logo_url):
        try:
            # CORRECCIÓN AQUÍ:
            # Cambiamos 'ACTIVO' por 1 (porque tu columna ESTADO es tipo BIT)
            sql = text("""
                INSERT INTO RESTAURANTE 
                (ID_DUENO, NOMBRE, DIRECCION, TELEFONO, OPENING_TIME, CLOSING_TIME, rutafotologo, ESTADO, FECHA_CREACION)
                VALUES 
                (:owner_id, :name, :address, :phone, :opening, :closing, :logo, 1, GETDATE())
            """)
            
            db.session.execute(sql, {
                'owner_id': owner_id,
                'name': name,
                'address': address,
                'phone': phone,
                'opening': opening_time,
                'closing': closing_time,
                'logo': logo_url
            })
            
            db.session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error creating restaurant in DB: {e}")
            db.session.rollback()
            raise e