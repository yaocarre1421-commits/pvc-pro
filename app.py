from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
import math

app = Flask(__name__)
app.secret_key = "clave_secreta"

# Archivos
USUARIOS_FILE = "usuarios_web.json"
CLIENTES_FILE = "clientes.json"

# -------------------------
# UTILIDADES
# -------------------------

def cargar_json(ruta):
    if not os.path.exists(ruta):
        with open(ruta, "w") as f:
            json.dump([], f)
    with open(ruta, "r") as f:
        return json.load(f)

def guardar_json(ruta, data):
    with open(ruta, "w") as f:
        json.dump(data, f, indent=4)

# -------------------------
# LOGIN
# -------------------------

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]

        usuarios = cargar_json(USUARIOS_FILE)

        for u in usuarios:
            if u["usuario"] == usuario and u["password"] == password:
                session["usuario"] = usuario
                return redirect(url_for("dashboard"))

        return "❌ Usuario o contraseña incorrectos"

    return render_template("login.html")

# -------------------------
# REGISTRO
# -------------------------

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]

        usuarios = cargar_json(USUARIOS_FILE)

        usuarios.append({
            "usuario": usuario,
            "password": password
        })

        guardar_json(USUARIOS_FILE, usuarios)

        return redirect(url_for("login"))

    return render_template("registro.html")

# -------------------------
# DASHBOARD + COTIZADOR
# -------------------------

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))

    resultado = None

    if request.method == "POST":
        ancho = float(request.form["ancho"])
        largo = float(request.form["largo"])

        ancho_lamina = float(request.form["ancho_lamina"])  # 0.25
        largo_lamina = float(request.form["largo_lamina"])  # 3 a 6

        orientacion = request.form["orientacion"]

        # AREA
        area = ancho * largo

        # CALCULO PROFESIONAL
        if orientacion == "largo":
            filas = math.ceil(ancho / ancho_lamina)
            columnas = math.ceil(largo / largo_lamina)
        else:
            filas = math.ceil(largo / ancho_lamina)
            columnas = math.ceil(ancho / largo_lamina)

        total_laminas = filas * columnas

        # DESPERDICIO
        area_total_laminas = total_laminas * (ancho_lamina * largo_lamina)
        desperdicio = area_total_laminas - area

        # RECORTES (estimado)
        recortes = total_laminas - (area / (ancho_lamina * largo_lamina))

        resultado = {
            "area": round(area, 2),
            "laminas": total_laminas,
            "filas": filas,
            "columnas": columnas,
            "desperdicio": round(desperdicio, 2),
            "recortes": round(recortes, 1)
        }

    return render_template("dashboard.html", resultado=resultado)

# -------------------------
# CLIENTES
# -------------------------

@app.route("/clientes", methods=["POST"])
def clientes():
    if "usuario" not in session:
        return redirect(url_for("login"))

    nombre = request.form["nombre"]
    telefono = request.form["telefono"]

    clientes = cargar_json(CLIENTES_FILE)

    clientes.append({
        "nombre": nombre,
        "telefono": telefono
    })

    guardar_json(CLIENTES_FILE, clientes)

    return redirect(url_for("dashboard"))

# -------------------------
# LOGOUT
# -------------------------

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))

# -------------------------
# INICIO
# -------------------------

if __name__ == "__main__":
    app.run(debug=True)