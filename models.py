# models.py
from flask_sqlalchemy import SQLAlchemy  # Importiert SQLAlchemy für die Datenbankverwaltung
import re  # Importiert reguläre Ausdrücke zur Validierung (z. B. von E-Mail-Adressen)

db = SQLAlchemy()

# Modell für die Benutzer-Tabelle
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

# Modell für die Kommentar-Tabelle (allgemeine Kommentare)
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    user = db.relationship('User', backref=db.backref('comments', lazy=True))

# Modell für die Zutaten-Tabelle
class Ingredient(db.Model):
    __tablename__ = "ingredients"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

# Modell für die Rezept-Tabelle
class Recipe(db.Model):
    __tablename__ = "recipes"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('recipes', lazy=True))

# Modell für die Verknüpfungstabelle zwischen Rezepten und Zutaten
class RecipeIngredient(db.Model):
    __tablename__ = "recipe_ingredients"
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50), nullable=False)
    recipe = db.relationship('Recipe', backref=db.backref('ingredients', lazy=True))
    ingredient = db.relationship('Ingredient', backref=db.backref('recipes', lazy=True))

# Modell für die Rezept-Kommentar-Tabelle
class RecipeComment(db.Model):
    __tablename__ = "recipe_comments"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(4096), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id', ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    user = db.relationship('User', backref=db.backref('recipe_comments', lazy=True))
    recipe = db.relationship('Recipe', backref=db.backref('recipe_comments', lazy=True))

# Funktion zur Validierung von E-Mail-Adressen
def is_valid_email(email):
    return re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email)