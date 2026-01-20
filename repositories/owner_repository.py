from BDD.db import db
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

class OwnerRepository:
    
    def get_restaurant_by_owner(self, owner_id):
        """Busca el ID del restaurante de este dueño"""
        try:
            sql = text("SELECT * FROM RESTAURANTE WHERE ID_DUENO = :uid")
            result = db.session.execute(sql, {'uid': owner_id}).fetchone()
            
            if result:
                # CORRECCIÓN: Usamos 'ID_RESTAURANTE' en lugar de 'ID'
                return {
                    'id': result.ID_RESTAURANTE, 
                    'nombre': result.NOMBRE,
                    'direccion': result.DIRECCION,
                    'rutafotologo': result.rutafotologo
                }
            return None
        except Exception as e:
            logger.error(f"Error getting restaurant: {e}")
            return None

    def get_menus(self, restaurant_id):
        try:
            # CORRECCIÓN: Usamos 'ID_RESTAURANTE' en el WHERE
            sql = text("SELECT * FROM MENU WHERE ID_RESTAURANTE = :rid")
            result = db.session.execute(sql, {'rid': restaurant_id})
            
            menus = []
            for row in result.fetchall():
                menus.append({
                    'id': row.ID_MENU,
                    'nombre': row.NOMBRE_PLATO,
                    'descripcion': row.DESCRIPCION,
                    'precio': float(row.PRECIO),
                    'disponible': row.DISPONIBLE,
                    'foto': row.rutafotomenu
                })
            return menus
        except Exception as e:
            logger.error(f"Error getting menus: {e}")
            return []

    def create_menu(self, restaurant_id, nombre, desc, precio, foto):
        try:
            sql = text("""
                INSERT INTO MENU (ID_RESTAURANTE, NOMBRE_PLATO, DESCRIPCION, PRECIO, DISPONIBLE, rutafotomenu)
                VALUES (:rid, :nom, :desc, :prec, 1, :foto)
            """)
            db.session.execute(sql, {'rid': restaurant_id, 'nom': nombre, 'desc': desc, 'prec': precio, 'foto': foto})
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e

    def delete_menu(self, menu_id):
        try:
            sql = text("DELETE FROM MENU WHERE ID_MENU = :mid")
            db.session.execute(sql, {'mid': menu_id})
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e

    def get_reservations_with_details(self, restaurant_id):
        try:
            # CORRECCIÓN: Aseguramos los nombres correctos ID_RESERVA, ID_RESTAURANTE, etc.
            sql = text("""
                SELECT 
                    R.ID_RESERVA,
                    R.FECHA_RESERVA,
                    R.CANTIDAD_PERSONAS,
                    R.METODO_PAGO,
                    R.ESTADO_PAGO,
                    U.NAME as CLIENTE_NOMBRE,
                    U.LASTNAME as CLIENTE_APELLIDO,
                    M.NOMBRE_PLATO,
                    M.PRECIO
                FROM RESERVA R
                JOIN LOGINDETAILS U ON R.ID_CLIENTE = U.ID
                LEFT JOIN MENU M ON R.ID_MENU = M.ID_MENU
                WHERE R.ID_RESTAURANTE = :rid
                ORDER BY R.FECHA_RESERVA DESC
            """)
            
            result = db.session.execute(sql, {'rid': restaurant_id})
            reservations = []
            for row in result.fetchall():
                # Calculamos el total de forma segura (si precio es null, usamos 0)
                precio_unitario = float(row.PRECIO) if row.PRECIO else 0
                total_calc = precio_unitario * row.CANTIDAD_PERSONAS

                reservations.append({
                    'id': row.ID_RESERVA,
                    'fecha': str(row.FECHA_RESERVA),
                    'personas': row.CANTIDAD_PERSONAS,
                    'metodo_pago': row.METODO_PAGO,
                    'estado_pago': row.ESTADO_PAGO,
                    'cliente': f"{row.CLIENTE_NOMBRE} {row.CLIENTE_APELLIDO}",
                    'plato': row.NOMBRE_PLATO or "Solo Mesa",
                    'total': total_calc
                })
            return reservations
        except Exception as e:
            logger.error(f"Error getting reservations: {e}")
            return []