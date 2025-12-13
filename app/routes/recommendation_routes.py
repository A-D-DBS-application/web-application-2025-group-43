from flask import Blueprint, render_template, redirect, url_for, session, abort
from app.plant_recommendation_engine import calculate_plant_rankings, validate_playfield_access
from app.models import RobotZone

recommendation_bp = Blueprint("recommendation", __name__, url_prefix="/recommendations")


@recommendation_bp.route("/<serial_number>")
def recommended_plants(serial_number):
    user_email = session.get("user_email")
    if not user_email:
        return redirect(url_for("auth.login"))

    # Validate that the user has access to this playfield
    if not validate_playfield_access(serial_number, user_email):
        abort(403)  # Forbidden

    # Get the current plant for the playfield
    robot_zone = RobotZone.query.filter_by(serial_number=serial_number).first()
    current_plant_name = robot_zone.plant_name if robot_zone else None

    # Get the full list of ranked plants
    plant_rankings = calculate_plant_rankings(serial_number)

    return render_template(
        "recommended_plants.html",
        serial_number=serial_number,
        plant_rankings=plant_rankings,
        current_plant_name=current_plant_name,
        last_robot_serial=session.get('last_robot_serial'),
    )

