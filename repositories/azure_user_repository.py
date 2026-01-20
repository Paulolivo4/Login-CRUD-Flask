import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import text
# IMPORTANTE: Agregamos generate_password_hash para la migración
from werkzeug.security import check_password_hash, generate_password_hash 

from BDD.db import db
from MODEL.models import LoginDetails
from repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

class AzureUserRepository(UserRepository):

    def get_all_users(self) -> List[Dict[str, Any]]:
        try:
            users = LoginDetails.query.all()
            return [u.to_dict() for u in users]
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []

    def create_user(self, user_entity) -> bool:
        try:
            new_user_orm = LoginDetails(
                NAME=user_entity.name,
                LASTNAME=user_entity.lastname,
                EMAIL=user_entity.email,
                PASSWORD=user_entity.password,
                ROL_ID=user_entity.role_id
            )
            db.session.add(new_user_orm)
            db.session.commit()
            return True
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            db.session.rollback()
            raise e

    def delete_user(self, email: str) -> bool:
        try:
            user = LoginDetails.query.filter_by(EMAIL=email).first()
            if user:
                db.session.delete(user)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            raise e

    def get_user_by_email(self, email: str):
        return LoginDetails.query.filter_by(EMAIL=email).first()

    def update_user(self, user_id, name, lastname, email, role_id):
        try:
            user = LoginDetails.query.filter_by(ID=user_id).first()
            if not user: raise ValueError("Usuario no encontrado")
            user.NAME = name
            user.LASTNAME = lastname
            user.EMAIL = email
            user.ROL_ID = role_id
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e

    # ==========================================================
    # LOGIN INTELIGENTE (Detecta + Migra)
    # ==========================================================
    def authenticate(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        try:
            # 1. Buscamos SOLO por email primero
            user = LoginDetails.query.filter_by(EMAIL=email).first()
            
            if not user:
                logger.warning(f"User not found: {email}")
                return None

            # Limpiamos espacios en blanco de la BD (común en SQL legacy)
            db_pass = user.PASSWORD.strip() if user.PASSWORD else ""

            # 2. Verificamos la contraseña
            password_valid = False
            migrated = False
            
            # CASO A: Usuario YA SEGURO (Hash)
            if db_pass.startswith('scrypt:') or db_pass.startswith('pbkdf2:'):
                if check_password_hash(db_pass, password):
                    password_valid = True
            
            # CASO B: Usuario VIEJO (Texto Plano)
            elif db_pass == password:
                password_valid = True
                # --- MIGRACIÓN AUTOMÁTICA ---
                try:
                    logger.info(f"Detectado usuario legacy: {email}. Encriptando contraseña...")
                    secure_hash = generate_password_hash(password)
                    user.PASSWORD = secure_hash
                    db.session.commit()
                    migrated = True
                    logger.info("Migración de seguridad exitosa.")
                except Exception as e:
                    logger.error(f"Error en migración automática: {e}")
                    # Si falla la migración, dejamos pasar al usuario igual, no bloqueamos
            
            if password_valid:
                logger.info(f"User authenticated: {email} {'(Migrated)' if migrated else ''}")
                return user.to_dict()
            else:
                logger.warning(f"Invalid password for: {email}")
                return None

        except Exception as e:
            logger.error(f"Auth error: {e}")
            return None

    def get_owners_without_restaurant(self):
        try:
            sql = text("""
                SELECT U.ID, U.NAME, U.LASTNAME, U.EMAIL 
                FROM LOGINDETAILS U
                LEFT JOIN RESTAURANTE R ON U.ID = R.ID_DUENO
                WHERE U.ROL_ID = 2 AND R.ID_DUENO IS NULL
            """)
            result = db.session.execute(sql)
            return result.fetchall()
        except Exception as e:
            logger.error(f"Error getting available owners: {e}")
            return []

    def update_user_email(self, user_id, email):
        try:
            user = LoginDetails.query.get(user_id)
            if user:
                user.EMAIL = email
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            raise e
    def update_user_password(self, email, hashed_password):
        try:
            # Asumiendo que tu tabla se llama LOGINDETAILS y la columna PASSWORD
            sql = text("UPDATE LOGINDETAILS SET PASSWORD = :pw WHERE EMAIL = :email")
            db.session.execute(sql, {'pw': hashed_password, 'email': email})
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error al actualizar password: {e}")
            return False
    
    def create_user_from_registration(self, name, lastname, email, password, role_id):
        try:
            # Usamos los nombres de columna que me pasaste: NAME, LASTNAME, EMAIL, PASSWORD, ROL_ID
            # No incluimos ID porque suele ser Autoincremental (Identity)
            sql = text("""
                INSERT INTO LOGINDETAILS (NAME, LASTNAME, EMAIL, PASSWORD, ROL_ID)
                VALUES (:name, :lastname, :email, :password, :role)
            """)
            
            db.session.execute(sql, {
                'name': name,
                'lastname': lastname,
                'email': email,
                'password': password,
                'role': role_id
            })
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            # Esto imprimirá el error real en tu consola de Flask
            print(f"--> ERROR SQL EN REGISTRO: {str(e)}")
            raise e