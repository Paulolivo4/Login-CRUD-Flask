from BDD.db import db
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

class ClientRepository:

    def get_all_restaurants(self):
        try:
            # Quitamos el WHERE para probar si trae algo
            sql = text("SELECT * FROM RESTAURANTE") 
            result = db.session.execute(sql)
            
            restaurants = []
            for row in result.fetchall():
                # Usamos ._mapping para acceder por nombre de columna de forma segura
                r = row._mapping 
                restaurants.append({
                    'id': r['ID_RESTAURANTE'], 
                    'nombre': r['NOMBRE'],
                    'direccion': r['DIRECCION'],
                    'foto': r['rutafotologo'],
                    'horario': f"{r['OPENING_TIME']} - {r['CLOSING_TIME']}"
                })
            
            print(f"--> [DEBUG] Restaurantes en BD: {len(restaurants)}")
            return restaurants
        except Exception as e:
            print(f"--> [ERROR SQL CLIENTE]: {e}")
            return []
    def get_menu_by_restaurant(self, restaurant_id):
        try:
            sql = text("SELECT * FROM MENU WHERE ID_RESTAURANTE = :rid AND DISPONIBLE = 1")
            result = db.session.execute(sql, {'rid': restaurant_id})
            menus = []
            for row in result.fetchall():
                menus.append({
                    'id': row.ID_MENU,
                    'nombre': row.NOMBRE_PLATO,
                    'descripcion': row.DESCRIPCION,
                    'precio': float(row.PRECIO),
                    'foto': row.rutafotomenu
                })
            return menus
        except Exception as e:
            return []

    def create_reservation(self, client_id, restaurant_id, menu_id, date, people, total, payment_method):
        try:
            # LIMPIEZA DE FECHA: Cambiamos la 'T' por un espacio para SQL Server
            clean_date = date.replace('T', ' ')
            
            sql = text("""
                INSERT INTO RESERVA 
                (ID_CLIENTE, ID_RESTAURANTE, ID_MENU, FECHA_RESERVA, CANTIDAD_PERSONAS, METODO_PAGO, ESTADO_PAGO, TOTAL)
                VALUES 
                (:cid, :rid, :mid, :date, :people, :method, 'PAGADO', :total)
            """)
            
            db.session.execute(sql, {
                'cid': client_id, 'rid': restaurant_id, 'mid': menu_id,
                'date': clean_date, # Usamos la fecha limpia
                'people': people, 'method': payment_method, 'total': total
            })
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e