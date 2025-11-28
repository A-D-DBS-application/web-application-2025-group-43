from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        # Maak tabellen aan (MVP)
        db.create_all()

        # ---- Registreer Blueprints ----
        from .routes.auth_routes import auth_bp
        app.register_blueprint(auth_bp)

        from .routes.garden_routes import garden_bp
        app.register_blueprint(garden_bp)

        # ---- Debug: print ALLE routes ----
        print("\n=============== ROUTES DIE FLASK ZIET ===============")
        print(app.url_map)
        print("====================================================\n")

    return app

