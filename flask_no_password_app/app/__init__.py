from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Database initialisatie
    db.init_app(app)

    # Tabellen aanmaken (alleen voor MVP)
    with app.app_context():
        db.create_all()

    # -----------------------------
    # 📌 Belangrijk: registreer routes
    # -----------------------------
    from .routes import main        # <-- import jouw blueprint
    app.register_blueprint(main)    # <-- blueprint activeren

    return app