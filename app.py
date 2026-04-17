from flask import Flask, render_template, request, redirect, url_for, session, send_file
import json, os, math
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = "clave_secreta"

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

        return "Datos incorrectos"

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
        usuarios.append({"usuario": usuario, "password": password})
        guardar_json(USUARIOS_FILE, usuarios)

        return redirect(url_for("login"))

    return render_template("registro.html")

# -------------------------
# DASHBOARD
# -------------------------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))

    resultado = None

    if request.method == "POST":
        ancho = float(request.form["ancho"])
        largo = float(request.form["largo"])
        ancho_lamina = float(request.form["ancho_lamina"])
        largo_lamina = float(request.form["largo_lamina"])
        orientacion = request.form["orientacion"]

        precio_m2 = float(request.form["precio_m2"])

        # AREA
        area = ancho * largo

        # LAMINAS
        if orientacion == "largo":
            filas = math.ceil(ancho / ancho_lamina)
            columnas = math.ceil(largo / largo_lamina)
        else:
            filas = math.ceil(largo / ancho_lamina)
            columnas = math.ceil(ancho / largo_lamina)

        laminas = filas * columnas

        # ESTRUCTURA
        separacion = 0.7  # 70 cm
        omegas = math.ceil(ancho / separacion) + 1

        perimetro = (ancho + largo) * 2

        angulos = math.ceil(perimetro / 2.40)
        cornisas = math.ceil(perimetro / 5.95)

        # FIJACIONES
        tornillos = laminas * 10
        clavos = omegas * 10

        # PRECIO
        total = area * precio_m2

        resultado = {
            "area": round(area, 2),
            "laminas": laminas,
            "filas": filas,
            "columnas": columnas,
            "omegas": omegas,
            "angulos": angulos,
            "cornisas": cornisas,
            "tornillos": tornillos,
            "clavos": clavos,
            "total": round(total, 0)
        }

        session["resultado"] = resultado

    return render_template("dashboard.html", resultado=resultado)

# -------------------------
# PDF
# -------------------------
@app.route("/pdf")
def generar_pdf():
    if "resultado" not in session:
        return redirect(url_for("dashboard"))

    r = session["resultado"]

    file = "cotizacion.pdf"
    c = canvas.Canvas(file)

    c.setFont("Helvetica", 12)

    y = 800
    c.drawString(50, y, "COTIZACIÓN PVC PRO")
    y -= 40

    for key, value in r.items():
        c.drawString(50, y, f"{key}: {value}")
        y -= 20

    c.save()

    return send_file(file, as_attachment=True)

# -------------------------
# CLIENTES
# -------------------------
@app.route("/clientes", methods=["POST"])
def clientes():
    nombre = request.form["nombre"]
    telefono = request.form["telefono"]

    clientes = cargar_json(CLIENTES_FILE)
    clientes.append({"nombre": nombre, "telefono": telefono})
    guardar_json(CLIENTES_FILE, clientes)

    return redirect(url_for("dashboard"))

# -------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)