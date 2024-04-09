from flask import Flask, redirect, url_for, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

app = Flask(__name__)
app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///empleado.sqlite3'

db = SQLAlchemy(app)

def actualizar_base_datos(objeto):
    db.session.add(objeto)
    db.session.commit()
    

class Empleado(db.Model):
    _nif = db.Column(db.String(9), primary_key=True)
    nombre = db.Column(db.String(100))
    telefono = db.Column(db.String(100))
    direccion = db.Column(db.String(300))
    fecha = db.Column(db.String(8))
    tipo = db.Column(db.String(50), nullable=False)    

    __mapper_args__ = {
        'polymorphic_identity': 'empleado',
        'polymorphic_on': tipo
    }

class Entrenador(Empleado):
    _nif = db.Column(db.String(9), db.ForeignKey('empleado._nif'), primary_key=True)
    fecha_inicio_entrenador = db.Column(db.String(8))

    __mapper_args__ = {
        'polymorphic_identity': 'entrenador'
    }

class Jugador(Empleado):
    _nif = db.Column(db.String(9), db.ForeignKey('empleado._nif'), primary_key=True)
    peso = db.Column(db.Integer)
    altura = db.Column(db.Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'jugador'
    }


@app.route("/")
def home():
    #query = (Empleado.query.paginate(page=start, per_page=size))

    empleados = Empleado.query.limit(100).all()
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
        
        empleado_existe = Empleado.query.filter_by(_nif=nif).first() is not None

        if empleado_existe:
            return "Ya existe un empleado con ese NIF", 400

        if especialidad == "jugador":
            empleado = Jugador(_nif=nif, fecha=fecha, nombre=nombre, telefono=telefono, direccion=direccion, tipo="jugador", altura=altura, peso=peso)
            actualizar_base_datos(empleado)
        elif especialidad == "entrenador":
            empleado = Entrenador(_nif=nif, fecha=fecha, nombre=nombre, telefono=telefono, direccion=direccion, tipo="entrenador", fecha_inicio_entrenador=fecha_contrato)
            actualizar_base_datos(empleado)
            return redirect(url_for("home"))
        else:
            return "Especialidad no es correcta", 400

    return render_template("insert.html")


@app.route("/eliminar", methods=["POST", "GET"])
def delete():
    if request.method == "POST":
        nif = request.form.get("nif")
        empleado = Empleado.query.get(nif)
        print(nif)
        print(empleado)

        if empleado:
            db.session.delete(empleado)
            db.session.commit()
            return redirect(url_for("home"))
        else:
            return "No existe ningun empleado con ese NIF", 400

    return render_template("delete.html")

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)