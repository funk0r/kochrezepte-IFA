# routes.py
from flask import render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Comment, Recipe, RecipeIngredient, Ingredient, RecipeComment, is_valid_email

def init_routes(app):
    @app.route("/", methods=["GET", "POST"])
    def index():
        if "user" not in session:
            return redirect(url_for("login"))
        user = User.query.filter_by(username=session["user"]).first()
        if not user:
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

    @app.route("/add_recipe", methods=["GET", "POST"])
    def add_recipe():
        if "user" not in session:
            return redirect(url_for("login"))
        user = User.query.filter_by(username=session["user"]).first()
        if not user:
            session.pop("user", None)
            return redirect(url_for("login"))
        ingredients = Ingredient.query.all()
        units = ["Stück", "Gramm", "Kilogramm", "Löffel", "Teelöffel", "Prise", "Liter", "dl", "ml"]
        if request.method == "POST":
            title = request.form["title"]
            instructions = request.form["instructions"]
            recipe = Recipe(title=title, instructions=instructions, user_id=user.id)
            db.session.add(recipe)
            db.session.commit()
            ingredient_ids = request.form.getlist("ingredient_id")
            amounts = request.form.getlist("amount")
            units_selected = request.form.getlist("unit")
            for i in range(len(ingredient_ids)):
                ingredient_id = ingredient_ids[i]
                amount = amounts[i]
                unit = units_selected[i]
                if ingredient_id and amount and unit:
                    recipe_ingredient = RecipeIngredient(
                        recipe_id=recipe.id,
                        ingredient_id=int(ingredient_id),
                        amount=float(amount),
                        unit=unit
                    )
                    db.session.add(recipe_ingredient)
            db.session.commit()
            return redirect(url_for("index"))
        return render_template("add_recipe.html", ingredients=ingredients, units=units)

    @app.route("/recipes")
    def list_recipes():
        if "user" not in session:
            return redirect(url_for("login"))
        recipes = Recipe.query.all()
        return render_template("recipes.html", recipes=recipes)

    @app.route("/recipe/<int:recipe_id>")
    def view_recipe(recipe_id):
        if "user" not in session:
            return redirect(url_for("login"))
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return "Rezept nicht gefunden!"
        ingredients = RecipeIngredient.query.filter_by(recipe_id=recipe.id).all()
        return render_template("recipe_detail.html", recipe=recipe, ingredients=ingredients)

    @app.route("/recipe/<int:recipe_id>/comment", methods=["POST"])
    def add_recipe_comment(recipe_id):
        if "user" not in session:
            return redirect(url_for("login"))
        user = User.query.filter_by(username=session["user"]).first()
        if not user:
            session.pop("user", None)
            return redirect(url_for("login"))
        content = request.form.get("content")
        if not content:
            return "Fehler: Kommentar darf nicht leer sein!"
        recipe_comment = RecipeComment(content=content, user_id=user.id, recipe_id=recipe_id)
        db.session.add(recipe_comment)
        db.session.commit()
        return redirect(url_for("view_recipe", recipe_id=recipe_id))

    # REST-API-Endpunkte
    @app.route("/api/recipes", methods=["GET"])
    def api_list_recipes():
        try:
            recipes = Recipe.query.all()
            recipes_data = [
                {
                    "id": recipe.id,
                    "title": recipe.title,
                    "instructions": recipe.instructions,
                    "user": recipe.user.username,
                    "ingredients": [
                        {
                            "name": ri.ingredient.name,
                            "amount": ri.amount,
                            "unit": ri.unit
                        } for ri in recipe.ingredients
                    ]
                } for recipe in recipes
            ]
            return {"recipes": recipes_data}, 200
        except Exception as e:
            return {"error": f"Fehler beim Abrufen der Rezepte: {str(e)}"}, 500

    @app.route("/api/recipes/<int:recipe_id>", methods=["GET"])
    def api_view_recipe(recipe_id):
        try:
            recipe = Recipe.query.get(recipe_id)
            if not recipe:
                return {"error": "Rezept nicht gefunden"}, 404
            recipe_data = {
                "id": recipe.id,
                "title": recipe.title,
                "instructions": recipe.instructions,
                "user": recipe.user.username,
                "ingredients": [
                    {
                        "name": ri.ingredient.name,
                        "amount": ri.amount,
                        "unit": ri.unit
                    } for ri in recipe.ingredients
                ]
            }
            return recipe_data, 200
        except Exception as e:
            return {"error": f"Fehler beim Abrufen des Rezepts: {str(e)}"}, 500