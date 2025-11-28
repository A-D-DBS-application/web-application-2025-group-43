# app/routes/garden_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..models import Garden
from .. import db
import uuid

garden_bp = Blueprint("garden", __name__, url_prefix="/garden")


# ===========================================
# CHECK LOGIN (helper)
# ===========================================
def require_login():
    if "user_email" not in session:
        flash("You must be logged in.", "error")
        return redirect(url_for("auth.login"))
    return None


# ===========================================
# 1. GARDEN SELECTION PAGE
# ===========================================
@garden_bp.route("/select")
def garden_selection():
    # Check login
    check = require_login()
    if check: return check

    user_email = session["user_email"]

    # Haal ALLE tuinen op voor deze user
    gardens = Garden.query.filter_by(user_email=user_email).all()

    return render_template("garden_selection.html", gardens=gardens)


# ===========================================
# 2. ADD GARDEN (GET + POST)
# ===========================================
@garden_bp.route("/add", methods=["GET", "POST"])
def add_garden():
    # Check login
    check = require_login()
    if check: return check

    if request.method == "POST":
        name = request.form.get("garden_name")
        address = request.form.get("address")
        size = request.form.get("size")

        if not name:
            flash("Garden name is required.", "error")
            return render_template("add_garden.html")

        new_garden = Garden(
            garden_id=uuid.uuid4(),
            garden_name=name,
            adress_garden=address,
            area_garden=size,
            user_email=session["user_email"],
        )

        db.session.add(new_garden)
        db.session.commit()

        flash("Garden added!", "success")
        return redirect(url_for("garden.garden_selection"))

    return render_template("add_garden.html")


# ===========================================
# 3. ENTER GARDEN → GO TO PLAYFIELDS (volgende pagina)
# ===========================================
@garden_bp.route("/<uuid:garden_id>")
def enter_garden(garden_id):
    # Check login
    check = require_login()
    if check: return check

    garden = Garden.query.filter_by(garden_id=garden_id).first()

    if not garden:
        flash("Garden not found.", "error")
        return redirect(url_for("garden.garden_selection"))

    # TEMPORARY: redirect to playfield page (you'll design this later)
    # We keep it simple:
    return redirect(url_for("playfield.playfield_selection", garden_id=garden_id))
