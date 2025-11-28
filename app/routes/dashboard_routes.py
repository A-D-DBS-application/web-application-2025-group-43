# app/routes/dashboard_routes.py
from math import pi

from flask import Blueprint, render_template, abort, session, redirect, url_for

from .. import db
from ..models import (
    User,
    Garden,
    RobotZone,
    Sensor,
    Measurement,
    Conclusion,
)

dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/dashboard"
)

SENSOR_KEYS = ["moisture", "temperature", "humidity", "rain", "light", "co2"]


def _get_current_user():
    """Haalt de ingelogde user uit de session. 
       Ik ga ervan uit dat je bij login: session['user_email'] = user.uemail zet.
    """
    user_email = session.get("user_email")
    if not user_email:
        return None
    return User.query.filter_by(uemail=user_email).first()


@dashboard_bp.route("/<serial_number>")
def dashboard(serial_number):
    # 1) Check of er iemand ingelogd is
    current_user = _get_current_user()
    if current_user is None:
        # geen user → terug naar login
        return redirect(url_for("auth.login"))

    # 2) Vind de robot / playfield
    robot = RobotZone.query.filter_by(serial_number=serial_number).first()
    if robot is None:
        abort(404)

    garden = robot.garden
    if garden is None or garden.user_email != current_user.uemail:
        # iemand probeert een tuin van een andere user te openen
        abort(403)

    # 3) Alle tuinen + playfields van deze user (voor de sidebar)
    user_gardens = (
        Garden.query
        .filter_by(user_email=current_user.uemail)
        .order_by(Garden.garden_name)
        .all()
    )

    sidebar_gardens = []
    for g in user_gardens:
        zones = sorted(g.robot_zones, key=lambda z: (z.robot_name or "").lower())
        sidebar_gardens.append({"garden": g, "zones": zones})

    # 4) Sensordata per type
    sensor_data = {}
    for key in SENSOR_KEYS:
        sensor = Sensor.query.filter_by(
            serial_number=serial_number,
            sensor_type=key,
        ).first()

        measurement = None
        series = []

        if sensor is not None:
            q = (
                Measurement.query
                .filter_by(srnr_sensor=sensor.srnr_sensor)
                .order_by(Measurement.time_m.desc())
            )
            measurement = q.first()
            series = list(reversed(q.limit(20).all()))

        sensor_data[key] = {
            "sensor": sensor,
            "measurement": measurement,
            "series": series,
        }

    # 5) Health score uit Conclusion
    conclusion = (
        Conclusion.query
        .filter_by(serial_number=serial_number)
        .order_by(Conclusion.calc_time.desc())
        .first()
    )

    if conclusion is not None and conclusion.concl_score is not None:
        try:
            health_score = int(float(conclusion.concl_score))
        except Exception:
            health_score = 92
    else:
        health_score = 92

    if health_score >= 90:
        health_label = "Uitstekende groeiomstandigheden"
    elif health_score >= 70:
        health_label = "Goede groeiomstandigheden"
    elif health_score >= 50:
        health_label = "Matige groeiomstandigheden"
    else:
        health_label = "Aandacht vereist"

    r = 52
    circumference = 2 * pi * r
    score_dasharray = circumference
    score_dashoffset = circumference * (1 - health_score / 100.0)

    return render_template(
        "dashboard.html",
        garden=garden,
        robot=robot,
        sidebar_gardens=sidebar_gardens,
        sensor_data=sensor_data,
        health_score=health_score,
        health_label=health_label,
        score_dasharray=score_dasharray,
        score_dashoffset=score_dashoffset,
        user_name=current_user.uname if current_user else "",
    )
