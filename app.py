from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import json
import os
import math  # 🔥 IMPORTANTE

app = Flask(__name__)
app.secret_key = "pvc_pro_secret"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

USUARIOS = "usuarios_web.json"
CLIENTES = "clientes.json"

# Crear archivos si no existen
for archivo in [USUARIOS, CLIENTES]:
    if not os.path.exists(archivo):
        with open(archivo, "w") as f:
            json.dump([], f)

# ========================
# 🔐 USUARIOS
# ========================
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

def cargar_usuarios():
    with open(USUARIOS, "r") as f:
        return json.load(f)

def guardar_usuarios(data):
    with open(USUARIOS, "w") as f:
        json.dump(data, f, indent=4)

# ========================
# 👤 CLIENTES
# ========================
def cargar_clientes():
    with open(CLIENTES, "r") as f:
        return json.load(f)

def guardar_clientes(data):
    with open(CLIENTES, "w") as f:
        json.dump(data, f, indent=4)

# ========================
# 🏠 DASHBOARD + COTIZADOR
# ========================
@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    clientes = cargar_clientes()
    resultado = None

    if request.method == "POST":
        ancho = float(request.form["ancho"])
        largo = float(request.form["largo"])

        area = ancho * largo
        perimetro = 2 * (ancho + largo)

        lam_ancho = float(request.form["lam_ancho"])
        lam_largo = float(request.form["lam_largo"])
        sep = float(request.form["sep"])
        omega_largo = float(request.form["omega_largo"])
        cornisa_largo = float(request.form["cornisa"])
        angulo_largo = float(request.form["angulo"])
        precio = float(request.form["precio"])
        clavos_m2 = float(request.form["clavos"])
        tornillos_m2 = float(request.form["tornillos"])

        # 🔥 CÁLCULOS PROFESIONALES
        laminas = math.ceil(ancho / lam_ancho) * math.ceil(largo / lam_largo)

        lineas = math.ceil(largo / sep)
        omegas = math.ceil((lineas * ancho) / omega_largo)

        cornisas = math.ceil(perimetro / cornisa_largo)
        angulos = math.ceil(perimetro / angulo_largo)

        clavos = math.ceil(area * clavos_m2)
        tornillos = math.ceil(area * tornillos_m2)

        total = area * precio

        resultado = {
            "area": round(area, 2),
            "laminas": laminas,
            "omegas": omegas,
            "cornisas": cornisas,
            "angulos": angulos,
            "clavos": clavos,
            "tornillos": tornillos,
            "total": int(total),
            "ancho": ancho,
            "largo": largo
        }

    return render_template("dashboard.html", clientes=clientes, resultado=resultado)

# ========================
# 🔐 LOGIN
# ========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["usuario"]
        pwd = request.form["password"]

        usuarios = cargar_usuarios()

        for u in usuarios:
            if u["usuario"] == user and u["password"] == pwd:
                login_user(User(user))
                return redirect(url_for("home"))

        return "Datos incorrectos"

    return render_template("login.html")

# ========================
# 📝 REGISTRO
# ========================
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        user = request.form["usuario"]
        pwd = request.form["password"]

        usuarios = cargar_usuarios()
        usuarios.append({"usuario": user, "password": pwd})
        guardar_usuarios(usuarios)

        return redirect(url_for("login"))

    return render_template("registro.html")

# ========================
# 👤 CLIENTES
# ========================
@app.route("/clientes", methods=["POST"])
@login_required
def clientes():
    nombre = request.form["nombre"]
    telefono = request.form["telefono"]

    data = cargar_clientes()
    data.append({"nombre": nombre, "telefono": telefono})
    guardar_clientes(data)

    return redirect(url_for("home"))

# ========================
# 🚪 LOGOUT
# ========================
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# ========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)