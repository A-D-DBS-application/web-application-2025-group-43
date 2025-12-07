from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from decimal import Decimal

from ..models import Garden, RobotZone, PlantProfile
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

    # Alle robot_zones (= playfields) voor deze garden
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

    # Get all available plants/crops for dropdown
    plants = PlantProfile.query.order_by(PlantProfile.display_name).all()

    if request.method == "POST":
        robot_name = request.form.get("robot_name")
        # area_playfield is voorlopig altijd 1 m²
        area = Decimal("1")
        serial = request.form.get("serial_number") or str(uuid.uuid4())
        plant_profile_id = request.form.get("plant_profile_id")

        if not robot_name:
            flash("Playfield name is required.", "error")
            return render_template("add_playfield.html", garden=garden, plants=plants)

        new_zone = RobotZone(
            serial_number=serial,
            area_playfield=area,
            robot_name=robot_name,
            garden_id=garden.garden_id,
            plant_profile_id=int(plant_profile_id) if plant_profile_id else None,
        )

        db.session.add(new_zone)
        db.session.commit()

        flash("Playfield added!", "success")
        return redirect(url_for("playfield.playfield_selection", garden_id=garden_id))

    return render_template("add_playfield.html", garden=garden, plants=plants)


@playfield_bp.route("/delete/<string:serial_number>/<uuid:garden_id>", methods=["POST"])
def delete_playfield(serial_number, garden_id):
    # zoek playfield
    zone = RobotZone.query.filter_by(serial_number=serial_number).first()

    if not zone:
        flash("Playfield not found.", "error")
        return redirect(url_for("playfield.playfield_selection", garden_id=garden_id))

    # delete cascade: sensors, measurements, feedback, health scores
    db.session.delete(zone)
    db.session.commit()

    flash("Playfield removed.", "success")
    return redirect(url_for("playfield.playfield_selection", garden_id=garden_id))


# =========================
# PLAYFIELD WIJZIGEN (EDIT)
# =========================
@playfield_bp.route("/edit/<string:serial_number>/<uuid:garden_id>", methods=["GET", "POST"])
def edit_playfield(serial_number, garden_id):
    check = require_login()
    if check:
        return check

    # garden ophalen
    garden = Garden.query.filter_by(garden_id=garden_id).first()
    if not garden:
        flash("Garden not found.", "error")
        return redirect(url_for("garden.garden_selection"))

    # playfield ophalen
    zone = RobotZone.query.filter_by(serial_number=serial_number).first()
    if not zone:
        flash("Playfield not found.", "error")
        return redirect(url_for("playfield.playfield_selection", garden_id=garden_id))

    # Get all available plants/crops for dropdown
    plants = PlantProfile.query.order_by(PlantProfile.display_name).all()

    # POST — formulier opslaan
    if request.method == "POST":
        zone.robot_name = request.form.get("robot_name")
        zone.area_playfield = request.form.get("area_playfield")
        plant_profile_id = request.form.get("plant_profile_id")
        zone.plant_profile_id = int(plant_profile_id) if plant_profile_id else None

        db.session.commit()

        flash("Playfield updated!", "success")
        return redirect(url_for("playfield.playfield_selection", garden_id=garden_id))

    # GET — formulier tonen met bestaande waarden
    return render_template(
        "edit_playfield.html",
        garden=garden,
        zone=zone,
        plants=plants,
    )
