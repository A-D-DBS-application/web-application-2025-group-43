# run.py - entry point voor je Flask app

from app import create_app

# Maak de Flask-app aan via de factory
app = create_app()

# Als dit script rechtstreeks wordt uitgevoerd, start de Flask-server
if __name__ == "__main__":
    app.run(debug=True)