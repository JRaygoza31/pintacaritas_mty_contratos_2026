from extensiones import db
from datetime import datetime
from sqlalchemy.sql import func

# ---------------------------
# MODELO EVENTO
# ---------------------------
class Evento(db.Model):
    __tablename__ = 'evento'

    id = db.Column(db.Integer, primary_key=True)
    tipo_evento = db.Column(db.String(50), nullable=False)  # Pintacaritas / Glitter
    nombre_cliente = db.Column(db.String(100), nullable=False)
    whatsapp = db.Column(db.String(50))
    fecha_evento = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.String(20))
    hora_termino = db.Column(db.String(20))
    cantidad_horas = db.Column(db.Float)
    servicios_interes = db.Column(db.Text)

    # 👉 Se mantiene como texto por ahora
    municipio = db.Column(db.String(50))
    tipo_fiesta = db.Column(db.String(50))

    nombre_salon = db.Column(db.String(100))
    direccion = db.Column(db.String(200))
    fecha_registro = db.Column(db.DateTime, default=func.now())

    # Campos administrativos
    folio_manual = db.Column(db.String(50))
    total = db.Column(db.Float)
    anticipo = db.Column(db.Float)
    restan = db.Column(db.Float)
    comentarios = db.Column(db.Text)


# ---------------------------
# MODELO SERVICIO
# ---------------------------
class Servicio(db.Model):
    __tablename__ = 'servicios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    materiales = db.Column(db.Text)
    tipo = db.Column(db.String(50))
    fecha_registro = db.Column(db.DateTime, default=func.now())

    def __repr__(self):
        return f"<Servicio {self.nombre} ({self.tipo})>"


# ---------------------------
# MODELO MUNICIPIO
# ---------------------------
class Municipio(db.Model):
    __tablename__ = 'municipios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    fecha_registro = db.Column(db.DateTime, default=func.now())

    def __repr__(self):
        return f"<Municipio {self.nombre}>"
# ---------------------------
# MODELO MUNICIPIO
# ---------------------------
class Tipo_fiesta(db.Model):
    __tablename__ = 'tipo_fiesta'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    fecha_registro = db.Column(db.DateTime, default=func.now())

    def __repr__(self):
        return f"<Municipio {self.nombre}>"



from flask_login import UserMixin
from extensiones import db

class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
