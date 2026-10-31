from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key-before-deployment")
DB = os.path.join(os.path.dirname(__file__), "perkins_kilian.db")

def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with connect() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL, phone TEXT, password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'client', created_at TEXT NOT NULL)""")
        con.execute("""CREATE TABLE IF NOT EXISTS requests(
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            service TEXT NOT NULL, business TEXT, details TEXT NOT NULL,
            budget TEXT, status TEXT NOT NULL DEFAULT 'Nouveau',
            created_at TEXT NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id))""")
        admin = con.execute("SELECT id FROM users WHERE email=?", ("admin@perkinskilian.ci",)).fetchone()
        if not admin:
            con.execute("INSERT INTO users(name,email,phone,password,role,created_at) VALUES(?,?,?,?,?,?)",
                ("Administrateur", "admin@perkinskilian.ci", "", generate_password_hash("ChangeMe123!"), "admin", datetime.now().isoformat(timespec="minutes")))

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Connectez-vous pour accéder à cet espace.", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Accès réservé à l’administration.", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

@app.context_processor
def inject_user():
    return {"current_user": session.get("name"), "current_role": session.get("role")}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name","").strip()
        email = request.form.get("email","").strip().lower()
        phone = request.form.get("phone","").strip()
        message = request.form.get("message","").strip()
        if not name or not email or not message:
            flash("Veuillez remplir votre nom, votre e-mail et votre message.", "error")
        else:
            # Store contact requests as a client inquiry by creating an account-less table entry.
            with connect() as con:
                con.execute("""CREATE TABLE IF NOT EXISTS messages(
                    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, phone TEXT,
                    message TEXT, created_at TEXT, status TEXT DEFAULT 'Nouveau')""")
                con.execute("INSERT INTO messages(name,email,phone,message,created_at) VALUES(?,?,?,?,?)",
                    (name,email,phone,message,datetime.now().isoformat(timespec="minutes")))
            flash("Merci ! Votre message a bien été envoyé. Notre équipe vous recontactera.", "success")
            return redirect(url_for("contact"))
    return render_template("contact.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name","").strip()
        email = request.form.get("email","").strip().lower()
        phone = request.form.get("phone","").strip()
        password = request.form.get("password","")
        if not name or not email or len(password) < 8:
            flash("Renseignez les champs et choisissez un mot de passe de 8 caractères minimum.", "error")
        else:
            try:
                with connect() as con:
                    con.execute("INSERT INTO users(name,email,phone,password,role,created_at) VALUES(?,?,?,?,?,?)",
                        (name,email,phone,generate_password_hash(password),"client",datetime.now().isoformat(timespec="minutes")))
                flash("Compte créé. Vous pouvez maintenant vous connecter.", "success")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("Cette adresse e-mail possède déjà un compte.", "error")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        with connect() as con:
            user = con.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if user and check_password_hash(user["password"], password):
            session.clear()
            session.update(user_id=user["id"], name=user["name"], role=user["role"])
            flash("Connexion réussie. Bienvenue !", "success")
            return redirect(url_for("admin_dashboard" if user["role"] == "admin" else "dashboard"))
        flash("Adresse e-mail ou mot de passe incorrect.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Vous êtes déconnecté.", "success")
    return redirect(url_for("home"))

@app.route("/espace-client")
@login_required
def dashboard():
    with connect() as con:
        requests = con.execute("SELECT * FROM requests WHERE user_id=? ORDER BY id DESC", (session["user_id"],)).fetchall()
    return render_template("dashboard.html", requests=requests)

@app.route("/demande", methods=["GET", "POST"])
@login_required
def new_request():
    if request.method == "POST":
        service = request.form.get("service","").strip()
        business = request.form.get("business","").strip()
        details = request.form.get("details","").strip()
        budget = request.form.get("budget","").strip()
        if not service or not details:
            flash("Choisissez un service et décrivez votre besoin.", "error")
        else:
            with connect() as con:
                con.execute("INSERT INTO requests(user_id,service,business,details,budget,created_at) VALUES(?,?,?,?,?,?)",
                    (session["user_id"],service,business,details,budget,datetime.now().isoformat(timespec="minutes")))
            flash("Votre demande a été envoyée à Perkins & Kilian.", "success")
            return redirect(url_for("dashboard"))
    return render_template("new_request.html")

@app.route("/admin")
@login_required
@admin_required
def admin_dashboard():
    with connect() as con:
        users = con.execute("SELECT id,name,email,phone,role,created_at FROM users ORDER BY id DESC").fetchall()
        requests = con.execute("""SELECT requests.*, users.name AS client_name, users.email AS client_email
            FROM requests JOIN users ON users.id=requests.user_id ORDER BY requests.id DESC""").fetchall()
        try:
            messages = con.execute("SELECT * FROM messages ORDER BY id DESC").fetchall()
        except sqlite3.OperationalError:
            messages = []
    return render_template("admin.html", users=users, requests=requests, messages=messages)

@app.route("/admin/demande/<int:request_id>", methods=["POST"])
@login_required
@admin_required
def update_request(request_id):
    status = request.form.get("status","Nouveau")
    if status not in ["Nouveau","En cours","Terminé","Annulé"]:
        status = "Nouveau"
    with connect() as con:
        con.execute("UPDATE requests SET status=? WHERE id=?", (status,request_id))
    flash("Statut de la demande mis à jour.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/message/<int:message_id>", methods=["POST"])
@login_required
@admin_required
def update_message(message_id):
    status = request.form.get("status","Nouveau")
    if status not in ["Nouveau","Lu","Traité"]:
        status = "Nouveau"
    with connect() as con:
        con.execute("UPDATE messages SET status=? WHERE id=?", (status,message_id))
    flash("Statut du message mis à jour.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/mentions-legales")
def legal():
    return render_template("legal.html")

init_db()
if __name__ == "__main__":
    app.run(debug=True)
