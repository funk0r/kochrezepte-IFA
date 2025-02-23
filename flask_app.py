from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
app.config["DEBUG"] = True

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="funk0r",
    password="Timbersaw2025!",
    hostname="funk0r.mysql.pythonanywhere-services.com",
    databasename="funk0r$kochrezepte",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'dein_geheimes_schluessel'

# Sicherstellen, dass MySQL nicht wegen Inaktivität trennt
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 280,
    "pool_pre_ping": True,
}

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    user = db.relationship('User', backref=db.backref('comments', lazy=True))

def is_valid_email(email):
    return re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email)

@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect(url_for("login"))

    user = User.query.filter_by(username=session["user"]).first()

    if not user:  # Falls der Benutzer nicht gefunden wird
        session.pop("user", None)
        return redirect(url_for("login"))

    if request.method == "POST":
        comment = Comment(content=request.form["contents"], user_id=user.id)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('index'))

    comments = Comment.query.order_by(Comment.id.desc()).all()
    return render_template("main_page.html", comments=comments, username=user.username)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if not username or not email or not password:
            return "Fehler: Alle Felder müssen ausgefüllt werden!"

        if not is_valid_email(email):
            return "Fehler: Ungültige E-Mail-Adresse!"

        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()
        if existing_user:
            return "Fehler: Benutzername existiert bereits!"
        if existing_email:
            return "Fehler: E-Mail-Adresse wird bereits verwendet!"

        try:
            hashed_password = generate_password_hash(password)
            user = User(username=username, email=email, password_hash=hashed_password)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("login"))
        except Exception as e:
            return f"Fehler beim Speichern in der Datenbank: {str(e)}"

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session["user"] = username
            return redirect(url_for("index"))
        return "Falscher Benutzername oder Passwort!"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/delete_user/<username>", methods=["POST"])
def delete_user(username):
    if "user" not in session or session["user"] != username:
        return "Nicht autorisiert!"
    
    user = User.query.filter_by(username=username).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        session.pop("user", None)
        return redirect(url_for("login"))
    return "Benutzer nicht gefunden!"

if __name__ == '__main__':
    app.run(debug=True)
