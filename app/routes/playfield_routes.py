from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from ..models import Garden, RobotZone
from .. import db
import uuid

playfield_bp = Blueprint("playfield", __name__, url_prefix="/playfield")

def require_login():
    if "user_email" not in session:
        flash("You must be logged in.", "error")
        return redirect(url_for("auth.login"))
    return None

# =========================
# OVERZICHT ALLE PLAYFIELDS
# =========================
@playfield_bp.route("/<uuid:garden_id>")
def playfield_selection(garden_id):
    check = require_login()
    if check:
        return check

    # Garden ophalen
    garden = Garden.query.filter_by(garden_id=garden_id).first()
    if not garden:
        flash("Garden not found.", "error")
        return redirect(url_for("garden.garden_selection"))

    # 🔥 Alle robot_zones (= playfields) voor deze garden
    robot_zones = RobotZone.query.filter_by(garden_id=garden_id).all()

    return render_template(
        "playfields.html",
        garden=garden,
        robot_zones=robot_zones,
    )

# =========================
# NIEUW PLAYFIELD TOEVOEGEN
# =========================
@playfield_bp.route("/<uuid:garden_id>/add", methods=["GET", "POST"])
def add_playfield(garden_id):
    check = require_login()
    if check:
        return check

    garden = Garden.query.filter_by(garden_id=garden_id).first()
    if not garden:
        flash("Garden not found.", "error")
        return redirect(url_for("garden.garden_selection"))

    if request.method == "POST":
        robot_name = request.form.get("robot_name")
        area = request.form.get("area_playfield")
        serial = request.form.get("serial_number") or str(uuid.uuid4())

        if not robot_name:
            flash("Playfield name is required.", "error")
            return render_template("add_playfield.html", garden=garden)

        new_zone = RobotZone(
            serial_number=serial,
            area_playfield=area,
            robot_name=robot_name,
            garden_id=garden.garden_id,
        )

        db.session.add(new_zone)
        db.session.commit()

        flash("Playfield added!", "success")
        return redirect(url_for("playfield.playfield_selection", garden_id=garden_id))

    return render_template("add_playfield.html", garden=garden)
