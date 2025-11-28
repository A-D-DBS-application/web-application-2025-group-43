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

        # ---- Blueprints registreren ----
        from .routes.auth_routes import auth_bp
        from .routes.garden_routes import garden_bp
        from .routes.playfield_routes import playfield_bp
        from .routes.dashboard_routes import dashboard_bp  # ✅

        app.register_blueprint(auth_bp)
        app.register_blueprint(garden_bp)
        app.register_blueprint(playfield_bp)
        app.register_blueprint(dashboard_bp)

        print("=============== ROUTES DIE FLASK ZIET ===============")
        print(app.url_map)
        print("====================================================")

    return app
