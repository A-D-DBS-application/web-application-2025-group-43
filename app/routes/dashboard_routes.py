# app/routes/dashboard_routes.py
from math import pi

from flask import Blueprint, render_template, abort, session, redirect, url_for

from .. import db
from ..models import User, Garden, RobotZone, Sensor, Measurement, Conclusion

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

# type-keys die we gebruiken
SENSOR_KEYS = ["moisture", "temperature", "humidity", "rain", "light", "co2"]


def _get_current_user():
    """Logged-in user uit de session halen.

    Bij login moet je dus iets doen zoals:
        session["user_email"] = user.uemail
    """
    user_email = session.get("user_email")
    if not user_email:
        return None
    return User.query.filter_by(uemail=user_email).first()


@dashboard_bp.route("/<serial_number>")
def dashboard(serial_number):
    # 1) User check
    current_user = _get_current_user()
    if current_user is None:
        return redirect(url_for("auth.login"))

    # 2) Robot / playfield vinden
    robot = RobotZone.query.filter_by(serial_number=serial_number).first()
    if robot is None:
        abort(404)

    garden = robot.garden
    if garden is None or garden.user_email != current_user.uemail:
        # iemand probeert tuin van andere user te openen
        abort(403)

    # 3) Gardens + playfields van deze user voor de sidebar
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

    # 4) Sensor-data per type
    sensor_data = {}

    for key in SENSOR_KEYS:
        sensor = (
            Sensor.query
            .filter_by(serial_number=serial_number, sensor_type=key)
            .first()
        )

        measurement = None
        series = []
        values = []
        labels = []

        if sensor is not None:
            q = (
                Measurement.query
                .filter_by(srnr_sensor=sensor.srnr_sensor)
                .order_by(Measurement.time_m.desc())
            )

            # hourly vs daily
            if key in ["rain", "light"]:
                limit = 7      # laatste 7 dagen
                fmt = "%d/%m"
            else:
                limit = 24     # laatste 24 uren
                fmt = "%H:%M"

            rows = list(q.limit(limit).all())
            if rows:
                measurement = rows[0]         # meest recente
                series = list(reversed(rows)) # chronologische volgorde

                for r in series:
                    try:
                        values.append(float(r.value))
                    except Exception:
                        values.append(None)
                    if r.time_m is not None:
                        labels.append(r.time_m.strftime(fmt))
                    else:
                        labels.append("")

        sensor_data[key] = {
            "sensor": sensor,
            "measurement": measurement,
            "series": series,
            "values": values,
            "labels": labels,
        }

    # 5) Health score uit laatste Conclusion
    latest_conclusion = (
        Conclusion.query
        .filter_by(serial_number=serial_number)
        .order_by(Conclusion.calc_time.desc())
        .first()
    )

    if latest_conclusion and latest_conclusion.concl_score is not None:
        try:
            health_score = int(float(latest_conclusion.concl_score))
        except Exception:
            health_score = 0
    else:
        health_score = 0

    if health_score >= 90:
        health_label = "Uitstekende groeiomstandigheden"
    elif health_score >= 70:
        health_label = "Goede groeiomstandigheden"
    elif health_score >= 50:
        health_label = "Matige groeiomstandigheden"
    else:
        health_label = "Aandacht vereist"

    # cirkelprogress voor health score
    r = 52
    circumference = 2 * pi * r
    score_dasharray = circumference
    score_dashoffset = circumference * (1 - health_score / 100.0)

    # 6) Health-trend: laatste 30 conclusies (dagelijks)
    trend_rows = list(
        reversed(
            list(
                Conclusion.query
                .filter_by(serial_number=serial_number)
                .order_by(Conclusion.calc_time.desc())
                .limit(30)
                .all()
            )
        )
    )

    health_trend_values = [
        float(row.concl_score)
        for row in trend_rows
        if row.concl_score is not None
    ]
    health_trend_labels = [
        row.calc_time.strftime("%d/%m")
        if row.calc_time is not None
        else ""
        for row in trend_rows
    ]

    # 7) Klein, JSON-vriendelijk object specifiek voor de grafieken
    chart_data = {
        key: {
            "values": sensor_data[key]["values"],
            "labels": sensor_data[key]["labels"],
        }
        for key in SENSOR_KEYS
    }

    return render_template(
        "dashboard.html",
        garden=garden,
        robot=robot,
        sidebar_gardens=sidebar_gardens,
        sensor_data=sensor_data,      # voor de grote cijfers / teksten
        chart_data=chart_data,        # voor de grafieken in JS
        health_score=health_score,
        health_label=health_label,
        score_dasharray=score_dasharray,
        score_dashoffset=score_dashoffset,
        health_trend_values=health_trend_values,
        health_trend_labels=health_trend_labels,
        user_name=current_user.uname if current_user else "",
    )
