from flask import Flask, redirect, url_for, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/insertar")
def insert():
    return render_template("insert.html")


@app.route("/eliminar")
def delete():
    return render_template("delete.html")

if __name__ == "__main__":
    app.run()