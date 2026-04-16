from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json
import os
import math

app = Flask(__name__)
app.secret_key = "pvc_pro_secret"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

USUARIOS_FILE = "usuarios.json"

# -------------------------
# CREAR USUARIOS BASE
# -------------------------
if not os.path.exists(USUARIOS_FILE):
    with open(USUARIOS_FILE, "w") as f:
        json.dump([
            {"usuario": "admin", "password": "1234", "rol": "admin"}
        ], f)

# -------------------------
# USER CLASS
# -------------------------
class User(UserMixin):
    def __init__(self, id, rol):
        self.id = id
        self.rol = rol

@login_manager.user_loader
def load_user(user_id):
    with open(USUARIOS_FILE) as f:
        users = json.load(f)

    for u in users:
        if u["usuario"] == user_id:
            return User(u["usuario"], u.get("rol", "user"))
    return None

def validar_usuario(user, password):
    with open(USUARIOS_FILE) as f:
        users = json.load(f)

    for u in users:
        if u["usuario"] == user and u["password"] == password:
            return u
    return None

# -------------------------
# LOGIN
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        user = request.form["usuario"]
        password = request.form["password"]

        u = validar_usuario(user, password)

        if u:
            login_user(User(u["usuario"], u.get("rol", "user")))
            return redirect("/")

    return render_template("login.html")

# -------------------------
# LOGOUT
# -------------------------
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

# -------------------------
# CREAR USUARIO (ADMIN)
# -------------------------
@app.route("/crear_usuario", methods=["POST"])
@login_required
def crear_usuario():

    if current_user.rol != "admin":
        return "No autorizado"

    nuevo = request.form["usuario"]
    password = request.form["password"]

    with open(USUARIOS_FILE) as f:
        users = json.load(f)

    users.append({
        "usuario": nuevo,
        "password": password,
        "rol": "user"
    })

    with open(USUARIOS_FILE, "w") as f:
        json.dump(users, f)

    return redirect("/")

# -------------------------
# DASHBOARD
# -------------------------
@app.route("/", methods=["GET", "POST"])
@login_required
def dashboard():

    resultado = ""

    if request.method == "POST":

        ancho = float(request.form["ancho"])
        largo = float(request.form["largo"])
        orientacion = request.form["orientacion"]

        ancho_lamina = float(request.form["ancho_lamina"])
        largo_lamina = float(request.form["largo_lamina"])

        separacion_omegas = float(request.form["separacion_omegas"])
        clavos_m2 = float(request.form["clavos_m2"])
        tornillos_m2 = float(request.form["tornillos_m2"])
        precio_m2 = float(request.form["precio_m2"])

        area = ancho * largo

        # ==================================================
        # 🔥 LÁMINAS CORRECTAS (REGLA REAL DE INSTALACIÓN)
        # ==================================================

        if orientacion == "largo":
            ancho_cobertura = ancho
            largo_corte = largo
        else:
            ancho_cobertura = largo
            largo_corte = ancho

        # tiras necesarias en el techo
        tiras = math.ceil(ancho_cobertura / ancho_lamina)

        # piezas que salen de una lámina completa
        piezas_por_lamina = math.floor(largo_lamina / largo_corte)

        if piezas_por_lamina <= 0:
            laminas = tiras
        else:
            laminas = math.ceil(tiras / piezas_por_lamina)

        # ==================================================

        cornisas = math.ceil((2 * (ancho + largo)) / 5.95)
        angulos = math.ceil((2 * (ancho + largo)) / 2.40)
        omegas = math.ceil(area / separacion_omegas)

        clavos = math.ceil(area * clavos_m2)
        tornillos = math.ceil(area * tornillos_m2)

        total = area * precio_m2

        resultado = f"""
👤 Usuario: {current_user.id}

📐 Área: {area} m²

🧱 Materiales:
- Láminas PVC: {laminas}
- Cornisas: {cornisas}
- Ángulos: {angulos}
- Omegas: {omegas}
- Clavos: {clavos}
- Tornillos: {tornillos}

💰 TOTAL: ${total}

📊 Orientación: {orientacion}
"""

    return render_template(
        "dashboard.html",
        resultado=resultado,
        usuario=current_user.id,
        rol=current_user.rol
    )

# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)