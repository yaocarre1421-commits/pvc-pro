from flask import Flask, render_template, request, redirect, url_for
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
# CREAR USUARIOS SI NO EXISTE
# -------------------------
if not os.path.exists(USUARIOS_FILE):
    with open(USUARIOS_FILE, "w") as f:
        json.dump([{"usuario": "admin", "password": "1234"}], f)

# -------------------------
# LOGIN
# -------------------------
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

def validar_usuario(user, password):
    with open(USUARIOS_FILE) as f:
        usuarios = json.load(f)

    for u in usuarios:
        if u["usuario"] == user and u["password"] == password:
            return True
    return False

# -------------------------
# CALCULAR LÁMINAS
# -------------------------
def calcular_laminas(ancho, largo, orientacion, ancho_lamina, largo_lamina):

    if orientacion == "largo":
        tiras = math.ceil(ancho / ancho_lamina)
        piezas = math.floor(largo_lamina / largo)
    else:
        tiras = math.ceil(largo / ancho_lamina)
        piezas = math.floor(largo_lamina / ancho)

    if piezas == 0:
        return 0

    return math.ceil(tiras / piezas)

# -------------------------
# DASHBOARD
# -------------------------
@app.route("/", methods=["GET", "POST"])
@login_required
def dashboard():

    resultado = ""

    if request.method == "POST":

        # ---------------- MEDIDAS ----------------
        ancho = float(request.form["ancho"])
        largo = float(request.form["largo"])
        orientacion = request.form["orientacion"]

        # ---------------- MATERIALES ----------------
        ancho_lamina = float(request.form["ancho_lamina"])
        largo_lamina = float(request.form["largo_lamina"])

        separacion_omegas = float(request.form["separacion_omegas"])
        largo_omega = float(request.form["largo_omega"])

        cornisa = float(request.form["cornisa"])
        angulo_perimetral = float(request.form["angulo_perimetral"])

        clavos_m2 = float(request.form["clavos_m2"])
        tornillos_m2 = float(request.form["tornillos_m2"])

        precio_m2 = float(request.form["precio_m2"])

        # ---------------- CÁLCULOS ----------------
        area = ancho * largo

        laminas = calcular_laminas(ancho, largo, orientacion, ancho_lamina, largo_lamina)

        perimetro = 2 * (ancho + largo)

        cornisas = math.ceil(perimetro / cornisa)
        angulos = math.ceil(perimetro / angulo_perimetral)

        omegas = math.ceil(area / (separacion_omegas * 1))

        clavos = math.ceil(area * clavos_m2)
        tornillos = math.ceil(area * tornillos_m2)

        costo = area * precio_m2

        # ---------------- RESULTADO ----------------
        resultado = f"""
👤 Cliente: {current_user.id}

📐 ÁREA TOTAL: {area} m²

🧱 MATERIALES:
- Láminas PVC: {laminas}
- Cornisas: {cornisas}
- Ángulos perimetrales: {angulos}
- Omegas: {omegas}
- Clavos: {clavos}
- Tornillos: {tornillos}

💰 COSTO TOTAL ESTIMADO:
${costo}

📊 Orientación: {orientacion}
"""

    return render_template("dashboard.html", resultado=resultado, usuario=current_user.id)

# -------------------------
# LOGIN
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        user = request.form["usuario"]
        password = request.form["password"]

        if validar_usuario(user, password):
            login_user(User(user))
            return redirect(url_for("dashboard"))

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
# EJECUTAR
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)