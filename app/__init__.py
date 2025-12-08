from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ✅ Alleen de extensie initialiseren, GEEN db.create_all() hier
    db.init_app(app)

    # ✅ Blueprints importeren
    from .routes.auth_routes import auth_bp
    from .routes.garden_routes import garden_bp
    from .routes.playfield_routes import playfield_bp
    from .routes.dashboard_routes import dashboard_bp
    from .routes.profile_routes import profile_bp

    # ✅ Blueprints registreren
    app.register_blueprint(auth_bp)
    app.register_blueprint(garden_bp)
    app.register_blueprint(playfield_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(profile_bp)

    return app
