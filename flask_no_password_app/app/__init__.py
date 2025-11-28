from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config

# SQLAlchemy object
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Laad configuratie

    # Initialiseer SQLAlchemy
    db.init_app(app)

    # Maak tabellen automatisch aan in de database (handig voor MVP)
    with app.app_context():
        db.create_all()

    # Hier kan je later je routes registreren
    # from .routes.user_routes import user_bp
    # app.register_blueprint(user_bp)

    return app
