from flask import Flask, render_template, request, url_for, session, flash
from flask_migrate import Migrate
from database import db
from werkzeug.utils import redirect
from models import Maceta, Usuario, Carrito, MacetaCarrito, Administracion
from werkzeug.utils import secure_filename
import os

app = Flask(__name__) 

USER_DB = 'postgres'
PASS_DB = 'admin'
URL_DB = 'localhost'
NAME_DB = 'PamelaArte'
FULL_URL_DB = f'postgresql://{USER_DB}:{PASS_DB}@{URL_DB}/{NAME_DB}'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
UPLOAD_FOLDER = 'static/img'
app.config['SQLALCHEMY_DATABASE_URI'] = FULL_URL_DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/img'

db.init_app(app)
migrate = Migrate()
migrate.init_app(app, db)

app.config['SECRET_KEY'] = 'admin123'

# Rutas de la pagina
@app.route('/')
def index():
    macetas = Maceta.query.all()
    nombre_usuario = session.get('usuario_nombre') # Obtener el nombre del usuario que tiene la sesion iniciada, si no hay nadie iniciado con sesion esto queda None, por eso no se ve
    return render_template('index.html', macetas=macetas, nombre_usuario=nombre_usuario) # Importante no equivocarse que es macetassss

@app.route('/ver/<int:id>')
def ver_maceta(id):
    maceta = Maceta.query.get_or_404(id)
    nombre_usuario = session.get('usuario_nombre')
    return render_template('macetero.html', maceta=maceta, nombre_usuario=nombre_usuario)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email') # Obtener lo escrito en el formulario con id email
        contraseña = request.form.get('contraseña') # Obtener lo escrito en el formulario con id contraseña
        usuario = Usuario.query.filter_by(email=email, contraseña=contraseña).first() # Filtra por email y contraseña iguales a los ingresados, obtiene el primero que encuentra
        if usuario: # Si obtiene algo de lo anterior, obtiene el objeto y de ese objeto deja almacenado su id, nombre y email en la sesion
            session['usuario_id'] = usuario.id # Cada uno de ej: 'usuario_id' es solo una etiqueta creada justo ahora para utilizarla con el id del objeto
            session['usuario_nombre'] = usuario.nombre
            session['usuario_email'] = usuario.email
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Correo o contraseña incorrectos.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear() # Del diccionario que hay en session elimina todo lo que hay
    return redirect(url_for('index'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST': # Si el metodo es post, es decir si se envia el formulario realiza esto
        nombre = request.form.get('nombre') # Obtiene el valor del campo nombre del formulario
        email = request.form.get('email')
        contraseña = request.form.get('contraseña')
        # Verificar si el email ya existe
        if Usuario.query.filter_by(email=email).first(): # Filtra en el campo de email por el email ingresado, luego devuelve el primer valor que encuentra, si lo encuentra devuelve el objeto, si no devuelve None
            return render_template('registro.html', error='El correo ya está registrado.')
        # Crear usuario y guardar en la base de datos
        nuevo_usuario = Usuario(nombre=nombre, email=email, contraseña=contraseña) # Crea un objeto con cada atributo con lo ingresado
        db.session.add(nuevo_usuario) # Agrega el objeto a la sesion
        db.session.commit() # Guarda los cambios en la base de datos

        return redirect(url_for('login'))
    return render_template('registro.html')


@app.route('/agregar_carrito', methods=['POST'])
def agregar_carrito():
    if 'usuario_id' not in session: # Como session queda como diccionario, revisa si en la session hay una llave llamada 'usuario_id', si no encuentra nada queda None y devuelve al login
        return redirect(url_for('login'))
    usuario_id = session['usuario_id'] # Obtiene el id del usuario, busca la llave, de esa llave obtiene el valor
    maceta_id = request.form.get('maceta_id') # Como es un formulario en el index, obtiene lo que hay en el campo que esta oculto de la maceta en cuestion
    cantidad = int(request.form.get('cantidad', 1)) # Obtiene del formulario la cantidad, si no hay nada por defecto ocupa un 1

    # Buscar el carrito del usuario, si no existe lo crea
    carrito = Carrito.query.filter_by(id_usuario=usuario_id).first() # Dentro de la bd busca un carrito con un id_usuario igual al id del usuario que tiene la sesion iniciada
    if not carrito: # Si lo de arriba queda None, no entraria a este if pero con not hace entrarlo con None, si si obtiene algo no entra y pasa ese if
        carrito = Carrito(id_usuario=usuario_id) # Entonces crea un objeto carrito y asigna su id_usuario el id de usuario con la sesion iniciada
        db.session.add(carrito) # Agrega el carrito a la sesion
        db.session.commit() # Guardar los cambios

    # Verificar si la maceta ya está en el carrito
    item = MacetaCarrito.query.filter_by(id_carrito=carrito.id, id_maceta=maceta_id).first() # Filtra en la tabla MacetaCarrito por un registro con id_carrito al que estamos ocupando ahora y con id_maceta igual a la maceta que se quiere agregar
    if item: # Si encuentra una coincidencia y devuelve el objeto de MacetaCarrito entra al este if
        item.cantidad_maceta += cantidad # Del objeto que obtuvimos que es el registro de MacetaCarrito, su campo cantidad maceta se cambia por la cantidad que tiene actualmente por la cantidad agregada
    else:
        item = MacetaCarrito(id_maceta=maceta_id, id_carrito=carrito.id, cantidad_maceta=cantidad) # Si no encuentra nada, crea una conexion entre la maceta y el carrito
        db.session.add(item) # Y ese item lo agrega a la session
    db.session.commit() # Y se guardan cambios
    flash("haz agregado una nueva mazeta a tu carrito") # Un mensaje (aun esta en test) para cuando el usuario tenga como identificado que agrego un objeto a su carrito
    return redirect(url_for('index'))


@app.route('/carrito')
def carrito():
    print('Session:', session)
    if 'usuario_id' not in session: # Busca en session la llave 'usuario_id', si no la encuentra redirige al login
        return redirect(url_for('login'))
    usuario_id = session['usuario_id'] # Aqui llega solo si encontro algo, de esa llave obtiene el id del usuario
    carrito = Carrito.query.filter_by(id_usuario=usuario_id).first() # Ahora busca el registro u objeto de carrito asociado a ese usuario por el id
    productos = [] # Crear un array de productos que van a ser la asociacion entre la Maceta y el Carrito
    if carrito: # Si existe un carrito asociado a un usuario entra a este if
        productos = MacetaCarrito.query.filter_by(id_carrito=carrito.id).all() # Guarda en el array cada de los registros donde coincide el id del carrito con el id del carrito obtenido
    return render_template('carrito.html', productos=productos)

@app.route('/eliminar_carrito/<int:maceta_carrito_id>', methods=['POST']) # El boton funciona en base al id de la conexion entre la maceta y el carrito
def eliminar_carrito(maceta_carrito_id): # A la funcion le llega el id de la conexion entre maceta y carrito
    item = MacetaCarrito.query.get_or_404(maceta_carrito_id) # En la tabla MacetaCarrito busca el registro con el id que le llego, si no lo encuentra devuelve un 404
    db.session.delete(item) # Elimina de la session ese registro de la base de datos
    db.session.commit() # Guarda cambios
    return redirect(url_for('carrito')) # Redirige la funcion del carrito para que se actualice la pagina

# Pagina de inicio de sesion de administracion
@app.route('/administracion_inicio')
def administracion_inicio():
    return render_template('administracion_inicio.html')

# Metodo para ver si el usuario que se colocó esta en la base de datos
@app.route('/verificar_usuario', methods=['POST'])
def verificar_usuario():
    rut = request.form.get('rut')
    contraseña = request.form.get('contraseña')
    administracion = Administracion.query.filter_by(rut=rut, contraseña=contraseña).first()
    if administracion:
        session['admin'] = True
        session['admin_nombre'] = administracion.nombre
        return redirect(url_for('administracion'))
    else:
        return render_template('administracion_inicio.html', error='RUT o contraseña incorrectos.')

# Pagina de la administracion
@app.route('/administracion')
def administracion():
    if not session.get('admin'):
        return redirect(url_for('index'))
    macetas = Maceta.query.order_by('id')
    return render_template('administracion.html', macetas=macetas)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Agregar una maceta
@app.route('/administracion_agregar', methods=['GET', 'POST'])
def administracion_agregar():
    if not session.get('admin'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        tipo = request.form.get('tipo')
        precio = request.form.get('precio')
        tamaño = request.form.get('tamaño')
        color = request.form.get('color')
        stock = request.form.get('stock')
        imagen_file = request.files.get('imagen')

        if imagen_file and allowed_file(imagen_file.filename):
            filename = secure_filename(imagen_file.filename)
            imagen_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            nueva_maceta = Maceta(
                nombre=nombre, tipo=tipo, precio=int(precio), tamaño=tamaño,
                color=color, stock=int(stock), imagen=f'img/{filename}'
            )
            db.session.add(nueva_maceta)
            db.session.commit()
            flash('Maceta agregada correctamente')
            return redirect(url_for('administracion'))

        else:
            flash('Archivo no permitido o faltan datos')
            return redirect(url_for('administracion_agregar'))
        
    return render_template('administracion_agregar.html')