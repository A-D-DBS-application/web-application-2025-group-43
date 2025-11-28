from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

        # ---- Registreer alle Blueprints ----
        from .routes.auth_routes import auth_bp
        app.register_blueprint(auth_bp)

        # Debug: laat alle routes zien
        print("ROUTES DIE FLASK ZIET:")
        print(app.url_map)

    return app

