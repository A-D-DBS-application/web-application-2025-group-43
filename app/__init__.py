from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from .translations import get_all_translations, get_translation
from .icons import get_plant_icon

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
    from .routes.recommendation_routes import recommendation_bp

    # ✅ Blueprints registreren
    app.register_blueprint(auth_bp)
    app.register_blueprint(garden_bp)
    app.register_blueprint(playfield_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(recommendation_bp)

    # ✅ Taal context processor voor templates
    @app.context_processor
    def inject_language_and_icons():
        lang = session.get('language', 'en')
        return {
            'lang': lang,
            'translations': get_all_translations(lang),
            't': lambda key: get_translation(key, lang),
            'icon_for_plant': get_plant_icon
        }

    # ✅ Route voor taal wisselen
    @app.route('/set-language/<language>')
    def set_language(language):
        if language in ['en', 'nl']:
            session['language'] = language
        return '', 204

    return app
