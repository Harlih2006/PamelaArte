from database import db

class Maceta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(255), nullable=False)
    precio = db.Column(db.Integer, nullable=False)
    tamaño = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    imagen = db.Column(db.String(255), nullable=False)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    contraseña = db.Column(db.String(255), nullable=False)
    # Relación uno a uno con Carrito
    carrito = db.relationship('Carrito', back_populates='usuario', uselist=False)

class Carrito(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    # Relación inversa
    usuario = db.relationship("Usuario", back_populates="carrito")
    macetas = db.relationship("MacetaCarrito", back_populates="carrito")

class MacetaCarrito(db.Model):
    id_maceta_carrito = db.Column(db.Integer, primary_key=True)
    id_maceta = db.Column(db.Integer, db.ForeignKey('maceta.id'), nullable=False)
    id_carrito = db.Column(db.Integer, db.ForeignKey('carrito.id'), nullable=False)
    cantidad_maceta = db.Column(db.Integer, nullable=False)
    # Relaciones
    carrito = db.relationship("Carrito", back_populates="macetas")
    macetas = db.relationship("Maceta")

class Administracion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    rut = db.Column(db.String(100), unique=True, nullable=False)
    contraseña = db.Column(db.String(255), nullable=False)