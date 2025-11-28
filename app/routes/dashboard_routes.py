# app/routes/dashboard_routes.py
from flask import Blueprint, render_template, redirect, url_for, session, flash
from ..models import Garden, RobotZone
from .. import db

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/<string:serial_number>")
def dashboard(serial_number):
    # Moet ingelogd zijn
    if "user_email" not in session:
        return redirect(url_for("auth.login"))

    # Huidig playfield/robot zoeken
    robot = RobotZone.query.filter_by(serial_number=serial_number).first()

    if not robot:
        flash("Playfield / robot werd niet gevonden.", "error")
        return redirect(url_for("garden.garden_selection"))

    # Bijhorende garden
    garden = getattr(robot, "garden", None)
    if garden is None:
        garden = Garden.query.get(robot.garden_id)

    # Sidebar-data: alle gardens + hun playfields
    gardens = Garden.query.all()
    sidebar_gardens = []
    for g in gardens:
        zones = RobotZone.query.filter_by(garden_id=g.garden_id).all()
        sidebar_gardens.append({"garden": g, "zones": zones})

    user_name = session.get("user_name")
    health_score = 92  # dummy voor nu

    return render_template(
        "dashboard.html",
        robot=robot,
        garden=garden,
        sidebar_gardens=sidebar_gardens,
        user_name=user_name,
        health_score=health_score,
    )
