# ...existing code...
from flask import render_template, Blueprint

bp = Blueprint("main", __name__)

@bp.route("/select-garden")
def select_garden():
    # vervang door echte data vanuit DB wanneer beschikbaar
    return render_template("select_garden.html")
# ...existing code...