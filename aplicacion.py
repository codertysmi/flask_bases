from flask import Flask, redirect, url_for, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from sqlalchemy.orm import DeclarativeBase


app = Flask(__name__)
app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///empleado.sqlite3'


def actualizar_base_datos(objeto):
    db.session.add(objeto)
    db.session.commit()
    
class Base(DeclarativeBase):
  pass

db = SQLAlchemy(app, model_class=Base)

#dos opciones o en varias tablas o de forma nativa 1

class Empleado(db.Model):
    __tablename__ = 'empleado'
    _nif = db.Column(db.String(9), primary_key=True)
    nombre = db.Column(db.String(100))
    telefono = db.Column(db.String(100))
    direccion = db.Column(db.String(300))
    fecha = db.Column(db.String(8))
    tipo = db.Column(db.String(50), nullable=False)    

    __mapper_args__ = {
        'polymorphic_on': tipo,
        'polymorphic_identity': 'empleado',
        'with_polymorphic':'*'
    }

class Entrenador(Empleado):
    __tablename__ = "entrenador"
    _nif = db.Column(db.String(9), db.ForeignKey('empleado._nif'), primary_key=True)
    fecha_inicio_entrenador = db.Column(db.String(8))

    __mapper_args__ = {
        'polymorphic_identity': 'entrenador'
    }

class Jugador(Empleado):
    __tablename__ = "jugador"
    _nif = db.Column(db.String(9), db.ForeignKey('empleado._nif'), primary_key=True)
    peso = db.Column(db.Integer)
    altura = db.Column(db.Integer)
    posicion = db.Column(db.String(50), nullable=False)    

    __mapper_args__ = {
        'polymorphic_identity': 'jugador',
    }

class Portero(Jugador):
    __tablename__ = "portero"
    #preguntar si dos clave primaria compuesta es correcta en especializacion doble
    _nif = db.Column(db.String(9), db.ForeignKey('empleado._nif'), db.ForeignKey('jugador._nif'),  primary_key=True)
    grado = db.Column(db.Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'portero'
    }

class Defensa(Jugador):
    __tablename__ = "defensa"
    #preguntar si dos clave primaria compuesta es correcta en especializacion doble
    _nif = db.Column(db.String(9), db.ForeignKey('empleado._nif'), db.ForeignKey('jugador._nif'),  primary_key=True)
    grado = db.Column(db.Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'defensa'
    }

class Delantero(Jugador):
    __tablename__ = "delantero"
    #preguntar si dos clave primaria compuesta es correcta en especializacion doble
    _nif = db.Column(db.String(9), db.ForeignKey('empleado._nif'), db.ForeignKey('jugador._nif'),  primary_key=True)
    grado = db.Column(db.Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'delantero'
    }

@app.route("/")
def home():
    #query = (Empleado.query.paginate(page=start, per_page=size))

    empleados = Empleado.query.limit(100).all()
    for empleado in empleados:
        if empleado.tipo == "jugador":
            print(empleado.posicion)

    #db.session.add(Jugador(_nif="12421", fecha="20/09/2092", nombre="asj", telefono="", direccion="", tipo="jugador", altura=170, peso=90))
    #db.session.commit()
    return render_template("index.html", empleados=empleados)


@app.route("/insertar", methods=["POST", "GET"])
def insert():
    if request.method == "POST":
        nif = request.form.get("nif")
        nombre = request.form.get("nombre")
        telefono = request.form.get("telefono")
        direccion = request.form.get("direccion")
        fecha = request.form.get("fecha")
        especialidad = request.form.get("especialidad")
        altura = request.form.get("altura")
        peso = request.form.get("peso")
        fecha_contrato = request.form.get("fecha_contrato")
        posicion = request.form.get("posicion")
        grado = request.form.get("grado")
        empleado_existe = Empleado.query.filter_by(_nif=nif).first() is not None

        if empleado_existe:
            return render_template("Error.html", error_message="Ya existe un empleado con ese NIF"),400 

        if especialidad == "jugador":
            match posicion:
                case "portero":
                    empleado = Portero(_nif=nif, fecha=fecha, nombre=nombre, telefono=telefono, direccion=direccion, tipo="jugador", posicion="portero", altura=altura, peso=peso, grado=grado)
                    actualizar_base_datos(empleado)
                case "defensa":
                    empleado = Defensa(_nif=nif, fecha=fecha, nombre=nombre, telefono=telefono, direccion=direccion, tipo="jugador", posicion="defensa", altura=altura, peso=peso, grado=grado)
                    actualizar_base_datos(empleado)
                case "delantero":
                    empleado = Delantero(_nif=nif, fecha=fecha, nombre=nombre, telefono=telefono, direccion=direccion, tipo="jugador", posicion="delantero", altura=altura, peso=peso, grado=grado)
                    actualizar_base_datos(empleado)
            return redirect(url_for("home"))

        elif especialidad == "entrenador":
            empleado = Entrenador(_nif=nif, fecha=fecha, nombre=nombre, telefono=telefono, direccion=direccion, tipo="entrenador", fecha_inicio_entrenador=fecha_contrato)
            actualizar_base_datos(empleado)
            return redirect(url_for("home"))
        else:
             return render_template("Error.html", error_message="Especialidad no es correcta"),400 

    return render_template("insert.html")


@app.route("/eliminar", methods=["POST", "GET"])
def delete():
    if request.method == "POST":
        nif = request.form.get("nif")
        empleado = Empleado.query.get(nif)

        if empleado:
            db.session.delete(empleado)
            db.session.commit()
            return redirect(url_for("home"))
        else:
            return render_template("Error.html", error_message="No existe ningun empleado con ese NIF"),400

    return render_template("delete.html")


@app.route("/modificar", methods=["POST", "GET"])
def modificar():
    if request.method == "POST":
        nif = request.form.get("nif")
        empleado = Empleado.query.filter_by(_nif=nif).first()
        return render_template("modify2.html", empleado=empleado)

    empleados = Empleado.query.limit(100).all()
    return render_template("modify.html", empleados=empleados)

@app.route("/cambiar")
def cambiar():
    if request.method == "POST":
        empleado = Empleado.query.filter_by(_nif=nif).first()
        nif = request.form.get("nif")
        nombre = request.form.get("nombre")
        empleado.modify(_nif=nif, nombre=nombre)
        actualizar_base_datos(empleado)
        return redirect(url_for("home"))



if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)