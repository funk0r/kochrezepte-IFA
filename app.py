# app.py
from flask import Flask
from config import Config
from models import db
from routes import init_routes

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Routen einbinden
init_routes(app)

if __name__ == '__main__':
    app.run(debug=True)