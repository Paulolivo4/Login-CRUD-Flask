"""
Definición centralizada de todos los modelos SQLAlchemy.
"""
import logging
from BDD.db import db

logger = logging.getLogger(__name__)


# ============ ROLES ============

class Rol(db.Model):
    __tablename__ = 'ROLES'
    ID_ROL = db.Column(db.Integer, primary_key=True)
    NOMBRE_ROL = db.Column(db.String(50), nullable=False)


# ============ USUARIOS ============

class LoginDetails(db.Model):
    __tablename__ = 'LOGINDETAILS'

    ID = db.Column(db.Integer, primary_key=True)
    NAME = db.Column(db.String(255), nullable=False)
    LASTNAME = db.Column(db.String(255), nullable=False)
    EMAIL = db.Column(db.String(255), unique=True, nullable=False)
    PASSWORD = db.Column(db.String(255), nullable=False)
    ROL_ID = db.Column(db.Integer, db.ForeignKey('ROLES.ID_ROL'), nullable=False)

    def to_dict(self):
        return {
            'ID': self.ID,
            'NAME': self.NAME,
            'LASTNAME': self.LASTNAME,
            'EMAIL': self.EMAIL,
            'PASSWORD': self.PASSWORD,
            'ROL_ID': self.ROL_ID,
        }


# ============ RESTAURANTES ============

class Restaurante(db.Model):
    __tablename__ = 'RESTAURANTE'
    ID_RESTAURANTE = db.Column(db.Integer, primary_key=True)
    ID_DUENO = db.Column(db.Integer)
    NOMBRE = db.Column(db.String(255))
    DIRECCION = db.Column(db.String(512))
    TELEFONO = db.Column(db.String(50))
    ESTADO = db.Column(db.Boolean, default=True)
    FECHA_CREACION = db.Column(db.String(50))


# ============ MENUS ============

class Menu(db.Model):
    __tablename__ = 'MENU'
    ID_MENU = db.Column(db.Integer, primary_key=True)
    ID_RESTAURANTE = db.Column(db.Integer, db.ForeignKey('RESTAURANTE.ID_RESTAURANTE'))
    NOMBRE_PLATO = db.Column(db.String(255), nullable=False)
    DESCRIPCION = db.Column(db.String(1024))
    PRECIO = db.Column(db.Float)
    DISPONIBLE = db.Column(db.Boolean, default=True)
    RUTAFOTOMENU = db.Column(db.String(2048))


# ============ PROMOCIONES ============

class Promocion(db.Model):
    __tablename__ = 'PROMOCIONES'
    ID = db.Column(db.Integer, primary_key=True)
    ID_RESTAURANTE = db.Column(db.Integer, db.ForeignKey('RESTAURANTE.ID_RESTAURANTE'))
    TITULO = db.Column(db.String(255))
    DESCRIPCION = db.Column(db.String(1024))
    DESCUENTO = db.Column(db.Float)
    FECHA_VIGENCIA = db.Column(db.String(50))


# ============ RESERVAS ============

class Reserva(db.Model):
    __tablename__ = 'RESERVA'
    ID_RESERVA = db.Column(db.Integer, primary_key=True)
    ID_CLIENTE = db.Column(db.Integer)
    ID_RESTAURANTE = db.Column(db.Integer)
    FECHA_RESERVA = db.Column(db.DateTime)
    CANTIDAD_PERSONAS = db.Column(db.Integer)
    ESTADO = db.Column(db.String(50))


__all__ = ['Rol', 'LoginDetails', 'Restaurante', 'Menu', 'Promocion', 'Reserva']
