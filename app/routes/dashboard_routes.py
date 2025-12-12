# app/routes/dashboard_routes.py
from math import pi
from datetime import datetime, date, timedelta
from sqlalchemy import func

from flask import Blueprint, render_template, abort, session, redirect, url_for, jsonify, request

from .. import db
from ..models import (
    User,
    Garden,
    RobotZone,
    Sensor,
    Measurement,
    PlantProfile,
    HealthScore,
)
from ..plant_recommendation_engine import (
    calculate_plant_rankings,
    get_top_recommendations,
    get_average_measurements,
    calculate_plant_health_score,
    validate_playfield_access,
    SENSOR_WEIGHTS,
)

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

SENSOR_KEYS = ["moisture", "temperature", "humidity", "rain", "light", "co2"]

# mapping sensor_key -> plant_profile kolommen + labels + tips
ALERT_CONFIG = {
    "moisture": {
        "label": "Bodemvochtigheid",
        "unit": "%",
        "mean_attr": "soil_moisture_mean",
        "std_attr": "soil_moisture_std",
        "icon": "💧",
        "tips": [
            "Controleer of de druppelirrigatie correct werkt",
            "Zorg voor goede drainage in het plantbed",
            "Verhoog watergift in droge periodes",
            "Verlaag watergift in regenperiodes",
            "Compactie in de grond kan wateropname belemmeren",
        ]
    },
    "temperature": {
        "label": "Temperatuur",
        "unit": "°C",
        "mean_attr": "temperature_mean",
        "std_attr": "temperature_std",
        "icon": "🌡️",
        "tips": [
            "Pas ventilatie aan om temperatuur te reguleren",
            "Toename in verwarming in koude nacht",
            "Zorg voor goede luchtcirculatie",
            "Controleer isolatie van de kas/serre",
            "Extreme temperatuurschommelingen schaden plantgroei",
        ]
    },
    "humidity": {
        "label": "Luchtvochtigheid",
        "unit": "%",
        "mean_attr": "humidity_mean",
        "std_attr": "humidity_std",
        "icon": "💨",
        "tips": [
            "Verhoog luchtvochtigheid via vernevelingen",
            "Verbeter ventilatie als luchtvochtigheid te hoog",
            "Ziekten gedijen bij hoge luchtvochtigheid (>80%)",
            "Te lage luchtvochtigheid (<40%) belemmert groei",
            "Controleer HVAC (Heating, Ventilation, Air Conditioning) systeem",
        ]
    },
    "rain": {
        "label": "Regenval (Waterbehoefte)",
        "unit": "mm/week",
        "mean_attr": "rain_mm_week_mean",
        "std_attr": "rain_mm_week_std",
        "icon": "🌧️",
        "tips": [
            "Pas irrigatie aan op basis van natuurlijke regenval",
            "Gebruik regenwater harvesting systems",
            "Controleer waterafvoer na zware regenval",
            "Voorkom waterstagnatie en wortelrot",
            "Monitor weersverwachtingen voor irrigatieplanning",
        ]
    },
    "light": {
        "label": "Licht (PPFD)",
        "unit": "µmol/m²/s",
        "mean_attr": "ppfd_mean",
        "std_attr": "ppfd_std",
        "icon": "☀️",
        "tips": [
            "Verhoog lichtintensiteit met extra grow lights",
            "PPFD is belangrijker dan duur - intensiteit primair",
            "Controleer hoogte van LED-lampen",
            "Reinig lensen/reflectoren voor optimale lichtopbrengst",
            "Seizoensverandering beïnvloedt natuurlijke lichtinval",
        ]
    },
    "co2": {
        "label": "CO₂",
        "unit": "ppm",
        "mean_attr": "co2_mean",
        "std_attr": "co2_std",
        "icon": "🌿",
        "tips": [
            "CO₂ concentratie: laag (<300) = groeibeperking",
            "Optimaal bereik: 400-1000 ppm (planttype afhankelijk)",
            "Verbeter ventilatie om CO₂ aan te vullen",
            "CO₂ bronnen: compost, decomposeren, CO₂ generatoren",
            "Hoge CO₂ (>1500 ppm) kan negatief zijn zonder meer licht",
        ]
    },
}



def _get_current_user():
    user_email = session.get("user_email")
    if not user_email:
        return None
    return User.query.filter_by(uemail=user_email).first()


def _classify_status(value, mean, std):
    """
    Geeft (severity, status_text, z-score) terug.
    severity: 'ok', 'warning', 'critical', 'unknown'
    """
    if value is None or mean is None or std is None:
        return "unknown", "Geen data", None

    try:
        v = float(value)
        m = float(mean)
        s = float(std)
    except Exception:
        return "unknown", "Geen data", None

    if s == 0:
        return "unknown", "Geen referentie", None

    z = abs((v - m) / s)

    if z < 1:
        return "ok", "Optimaal", z
    elif z < 2:
        return "warning", "Lichte afwijking", z
    else:
        return "critical", "Sterke afwijking", z


def _calculate_quality_score(value, mean, std):
    """
    Calculate a quality score (0-100) for a sensor measurement based on
    how well it matches the optimal range.
    
    Uses the same quadratic penalty formula as the plant recommendation engine.
    
    Args:
        value (float): Current measurement value
        mean (float): Optimal mean value
        std (float): Standard deviation (tolerance)
    
    Returns:
        float: Quality score 0-100, or None if invalid data
    """
    if value is None or mean is None or std is None:
        return None
    
    try:
        v = float(value)
        m = float(mean)
        s = float(std)
    except Exception:
        return None
    
    if s == 0:
        return None
    
    # Calculate deviation in standard deviations
    x = abs((v - m) / s)
    
    # Apply quadratic penalty: score = max(0, 1 - x²) × 100
    quality = max(0, 1 - (x ** 2)) * 100
    return round(quality, 1)

def _calculate_daily_health_score(robot, sensor_data):
    """
    Berekent de dagelijkse gezondheidsscore volgens de formule:
    
    HealthScore = round(100 * sum(w_v * max(0, 1 - (|m_v - opt_v| / dev_v)^2)) / sum(w_v))
    
    Returns: float (0-100) of None als onvoldoende data
    """
    plant_profile = robot.plant_profile
    if plant_profile is None:
        return None
    
    scores = {}
    total_weight = 0
    weighted_sum = 0
    
    for key in SENSOR_KEYS:
        cfg = ALERT_CONFIG.get(key)
        meas = sensor_data[key]["measurement"]
        
        if meas is None:
            continue
        
        try:
            m_v = float(meas.value)  # meetwaarde
        except:
            continue
        
        # Haal optimale waarde (opt_v) en tolerantie (dev_v) op
        opt_v = getattr(plant_profile, cfg["mean_attr"], None)
        dev_v = getattr(plant_profile, cfg["std_attr"], None)
        
        if opt_v is None or dev_v is None or dev_v == 0:
            continue
        
        try:
            opt_v = float(opt_v)
            dev_v = float(dev_v)
        except:
            continue
        
        # Berekening:
        # d_v = |m_v - opt_v|  (afstand tot optimale waarde)
        # x_v = d_v / dev_v    (genormaliseerde afwijking)
        # s_v = max(0, 1 - x_v^2)  (score met quadratische straf)
        
        d_v = abs(m_v - opt_v)
        x_v = d_v / dev_v
        s_v = max(0, 1 - (x_v ** 2))
        
        scores[key] = s_v
        weight = 1.0  # MVP: alle gewichten 1.0
        weighted_sum += weight * s_v
        total_weight += weight
    
    if total_weight == 0:
        return None
    
    # Gemiddelde score normaliseren naar 0-100
    s_raw = weighted_sum / total_weight
    health_score = round(100 * s_raw)
    
    return health_score


def _get_health_trend_data(serial_number, period='month'):
    """
    Haalt gezondheid trend data op voor de opgegeven periode.
    
    period: 'week', 'month', 'quarter' (3 maanden), 'year'
    
    Returns: {
        'values': [scores],
        'labels': [dates],
        'trend_percent': +/-X% (vergelijking met vorige periode),
        'trend_direction': 'up' of 'down',
        'period_label': 'Laatste 7 dagen' etc
    }
    """
    today = date.today()
    
    # Bepaal date range en label format
    if period == 'week':
        days = 7
        compare_days = 7
        period_label = "Laatste 7 dagen"
        fmt = "%d/%m"  # Day/Month
        label_step = 1  # Show every day
    elif period == 'month':
        days = 30
        compare_days = 30
        period_label = "Laatste 30 dagen"
        fmt = "%d/%m"  # Day/Month
        label_step = 5  # Show every 5 days
    elif period == 'quarter':
        days = 90
        compare_days = 90
        period_label = "Laatste 3 maanden"
        fmt = "%d/%m"  # Day/Month
        label_step = 10  # Show every 10 days
    elif period == 'year':
        days = 365
        compare_days = 365
        period_label = "Afgelopen jaar"
        fmt = "%d/%m"  # Day/Month
        label_step = 30  # Show every 30 days (monthly)
    else:
        days = 30
        period_label = "Laatste 30 dagen"
        fmt = "%d/%m"
        label_step = 5
    
    # Haal huidige periode op
    start_date = today - timedelta(days=days)
    current_scores = (
        HealthScore.query.filter_by(serial_number=serial_number)
        .filter(HealthScore.calculated_at >= datetime.combine(start_date, datetime.min.time()))
        .filter(HealthScore.calculated_at <= datetime.combine(today, datetime.max.time()))
        .order_by(HealthScore.calculated_at.asc())
        .all()
    )
    
    # Haal vorige periode op (voor trend berekening)
    prev_end_date = start_date - timedelta(days=1)
    prev_start_date = prev_end_date - timedelta(days=compare_days)
    previous_scores = (
        HealthScore.query.filter_by(serial_number=serial_number)
        .filter(HealthScore.calculated_at >= datetime.combine(prev_start_date, datetime.min.time()))
        .filter(HealthScore.calculated_at <= datetime.combine(prev_end_date, datetime.max.time()))
        .order_by(HealthScore.calculated_at.asc())
        .all()
    )
    
    # Bereken gemiddelden
    current_avg = (
        sum(s.score for s in current_scores) / len(current_scores)
        if current_scores else None
    )
    previous_avg = (
        sum(s.score for s in previous_scores) / len(previous_scores)
        if previous_scores else None
    )
    
    # Bereken trend percentage
    if current_avg is not None and previous_avg is not None and previous_avg != 0:
        trend_percent = round(((current_avg - previous_avg) / previous_avg) * 100)
        trend_direction = "up" if trend_percent > 0 else "down"
    else:
        trend_percent = 0
        trend_direction = "neutral"
    
    # Formatteer data voor grafiek met intelligent label spacing
    values = [float(s.score) for s in current_scores]
    all_dates = [s.calculated_at.date() if s.calculated_at else s.score_date for s in current_scores]
    
    # Create labels with intelligent spacing based on period
    labels = []
    for i, dt in enumerate(all_dates):
        if i % label_step == 0 or i == len(all_dates) - 1:
            labels.append(dt.strftime(fmt))
        else:
            labels.append("")
    
    return {
        'values': values,
        'labels': labels,
        'trend_percent': abs(trend_percent),
        'trend_direction': trend_direction,
        'period_label': period_label,
        'current_avg': round(current_avg) if current_avg else 0,
        'previous_avg': round(previous_avg) if previous_avg else 0,
    }


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
        abort(403)

    # 3) Gardens + playfields van deze user voor de sidebar
    user_gardens = (
        Garden.query.filter_by(user_email=current_user.uemail)
        .order_by(Garden.garden_name)
        .all()
    )

    sidebar_gardens = []
    for g in user_gardens:
        zones = sorted(g.robot_zones, key=lambda z: (z.robot_name or "").lower())
        sidebar_gardens.append({"garden": g, "zones": zones})

    # 4) Sensor-data per type
    sensor_data = {}
    
    # Get plant profile early for use in sensor loop
    plant_profile = robot.plant_profile  # kan None zijn

    for key in SENSOR_KEYS:
        sensor = (
            Sensor.query.filter_by(serial_number=serial_number, sensor_type=key)
            .first()
        )

        measurement = None
        series = []
        values = []
        labels = []

        if sensor is not None:
            q = (
                Measurement.query.filter_by(srnr_sensor=sensor.srnr_sensor)
                .order_by(Measurement.time_m.desc())
            )

            # hourly vs daily
            if key in ["rain", "light"]:
                limit = 7
                fmt = "%d/%m"
            else:
                limit = 24
                fmt = "%H:%M"

            rows = list(q.limit(limit).all())
            if rows:
                measurement = rows[0]
                series = list(reversed(rows))

                for r in series:
                    try:
                        values.append(float(r.value))
                    except Exception:
                        values.append(None)

                    if r.time_m is not None:
                        labels.append(r.time_m.strftime(fmt))
                    else:
                        labels.append("")

        # Get optimal values from plant profile if available
        cfg = ALERT_CONFIG.get(key)
        optimal_mean = None
        optimal_std = None
        if plant_profile and cfg:
            optimal_mean = getattr(plant_profile, cfg["mean_attr"], None)
            optimal_std = getattr(plant_profile, cfg["std_attr"], None)

        sensor_data[key] = {
            "sensor": sensor,
            "measurement": measurement,
            "series": series,
            "values": values,
            "labels": labels,
            "optimal_mean": optimal_mean,
            "optimal_std": optimal_std,
        }

    # 5) Alerts & factor status op basis van PlantProfile
    alerts = []
    factor_states = {}

    for key in SENSOR_KEYS:
        cfg = ALERT_CONFIG.get(key)
        meas = sensor_data[key]["measurement"]
        value = float(meas.value) if meas is not None else None

        mean = getattr(plant_profile, cfg["mean_attr"], None) if plant_profile else None
        std = getattr(plant_profile, cfg["std_attr"], None) if plant_profile else None

        severity, status_text, z = _classify_status(value, mean, std)
        quality_score = _calculate_quality_score(value, mean, std)

        factor_states[key] = {
            "severity": severity,
            "status_text": status_text,
            "z": z,
            "mean": mean,
            "std": std,
            "quality_score": quality_score,
        }

        if severity in ("warning", "critical"):
            if value is not None and mean is not None:
                direction = "hoger" if value > mean else "lager"
            else:
                direction = "afwijkend"

            if z is not None:
                msg = f"{direction.capitalize()} dan ideaal (z={z:.2f})."
            else:
                msg = f"{direction.capitalize()} dan ideaal."

            alerts.append(
                {
                    "severity": severity,
                    "variable": cfg["label"],
                    "unit": cfg["unit"],
                    "value": round(value, 1) if value is not None else None,
                    "target": (
                        f"{mean:.1f} ± {std:.1f} {cfg['unit']}"
                        if mean is not None and std is not None
                        else "n.v.t."
                    ),
                    "message": msg,
                    "sensor_type": key,
                }
            )

    # 5.5) Bereken nieuwe health score op basis van formule
    calculated_health_score = _calculate_daily_health_score(robot, sensor_data)
    
    # Sla health score op voor vandaag (als nog niet gedaan)
    if calculated_health_score is not None:
        today = date.today()
        existing_score = (
            HealthScore.query.filter_by(
                serial_number=serial_number,
                score_date=today
            )
            .first()
        )
        
        if existing_score is None:
            # Maak nieuwe health score record aan
            new_health_score = HealthScore(
                serial_number=serial_number,
                score=calculated_health_score,
                score_date=today,
                calculated_at=datetime.now(),
            )
            db.session.add(new_health_score)
            db.session.commit()
        else:
            # Update bestaande record
            existing_score.score = calculated_health_score
            existing_score.calculated_at = datetime.now()
            db.session.commit()

    # 6) Health score uit database
    if calculated_health_score is not None:
        health_score = int(calculated_health_score)
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

    r = 52
    circumference = 2 * pi * r
    score_dasharray = circumference
    score_dashoffset = circumference * (1 - health_score / 100.0)

    # 7) Health-trend (gebruik HealthScore records - de afgelopen 30 dagen met proper dating)
    trend_rows = list(
        reversed(
            list(
                HealthScore.query.filter_by(serial_number=serial_number)
                .order_by(HealthScore.calculated_at.desc())
                .limit(30)
                .all()
            )
        )
    )

    health_trend_values = [
        float(row.score)
        for row in trend_rows
        if row.score is not None
    ]
    health_trend_labels = [
        row.calculated_at.strftime("%d/%m") if row.calculated_at is not None else ""
        for row in trend_rows
    ]

    # 7.5) Trend data voor standaard periode (month)
    trend_data = _get_health_trend_data(serial_number, period='month')

    # 8) Plant recommendations - from database PlantProfile
    plant_recommendations = []
    try:
        avg_measurements = get_average_measurements(serial_number, days=5)
        if avg_measurements:
            # Get all plant profiles from database
            from app.models import PlantProfile
            all_plants = PlantProfile.query.all()
            
            plant_rankings = []
            for plant in all_plants:
                # Convert PlantProfile to dict format for scoring
                plant_data = {
                    'moisture_mean': plant.soil_moisture_mean,
                    'moisture_std': plant.soil_moisture_std,
                    'temperature_mean': plant.temperature_mean,
                    'temperature_std': plant.temperature_std,
                    'humidity_mean': plant.humidity_mean,
                    'humidity_std': plant.humidity_std,
                    'rain_mean': plant.rain_mm_week_mean,
                    'rain_std': plant.rain_mm_week_std,
                    'light_mean': plant.ppfd_mean,
                    'light_std': plant.ppfd_std,
                    'co2_mean': plant.co2_mean,
                    'co2_std': plant.co2_std,
                }
                score = calculate_plant_health_score(avg_measurements, plant_data)
                if score is not None:
                    plant_rankings.append({
                        'key': plant.key,
                        'name': plant.display_name,
                        'icon': '🌱',  # Default icon since DB doesn't have emoji
                        'score': round(score, 2)
                    })
            plant_rankings.sort(key=lambda x: x['score'], reverse=True)
            plant_recommendations = plant_rankings[:3]  # Top 3 plants
    except Exception as e:
        print(f"Error calculating plant recommendations: {e}")
        import traceback
        traceback.print_exc()
        plant_recommendations = []

    # 9) Voor de grafieken
    chart_data = {
        key: {
            "values": sensor_data[key]["values"],
            "labels": sensor_data[key]["labels"],
        }
        for key in SENSOR_KEYS
    }

    # Store current dashboard serial for profile back button
    session['last_robot_serial'] = serial_number

    return render_template(
        "dashboard.html",
        garden=garden,
        robot=robot,
        sidebar_gardens=sidebar_gardens,
        sensor_data=sensor_data,
        chart_data=chart_data,
        health_score=health_score,
        health_label=health_label,
        score_dasharray=score_dasharray,
        score_dashoffset=score_dashoffset,
        health_trend_values=health_trend_values,
        health_trend_labels=health_trend_labels,
        trend_data=trend_data,
        user_name=current_user.uname if current_user else "",
        alerts=alerts,
        factor_states=factor_states,
        plant_recommendations=plant_recommendations,
    )


@dashboard_bp.route("/<serial_number>/health-trend-api", methods=["GET"])
def health_trend_api(serial_number):
    """
    API endpoint voor dynamische trend data.
    Query parameter: ?period=week|month|quarter|year
    """
    # User check
    current_user = _get_current_user()
    if current_user is None:
        return jsonify({"error": "Unauthorized"}), 401

    # Robot check
    robot = RobotZone.query.filter_by(serial_number=serial_number).first()
    if robot is None:
        return jsonify({"error": "Robot not found"}), 404

    # Permissions check
    garden = robot.garden
    if garden is None or garden.user_email != current_user.uemail:
        return jsonify({"error": "Forbidden"}), 403

    # Get period from query param
    period = request.args.get("period", "month")
    if period not in ["week", "month", "quarter", "year"]:
        period = "month"

    # Get trend data
    trend_data = _get_health_trend_data(serial_number, period=period)

    return jsonify(trend_data)


@dashboard_bp.route("/<serial_number>/sensor/<sensor_type>")
def sensor_detail(serial_number, sensor_type):
    """
    Detailpagina voor een specifieke sensor met uitgebreide grafiek, 
    alerts en advies.
    """
    # 1) User check
    current_user = _get_current_user()
    if current_user is None:
        return redirect(url_for("auth.login"))

    # 2) Validate sensor type
    if sensor_type not in SENSOR_KEYS:
        abort(404)

    # 3) Robot check
    robot = RobotZone.query.filter_by(serial_number=serial_number).first()
    if robot is None:
        abort(404)

    # 4) Permissions check
    garden = robot.garden
    if garden is None or garden.user_email != current_user.uemail:
        abort(403)

    # 5) Get sidebar gardens
    user_gardens = (
        Garden.query.filter_by(user_email=current_user.uemail)
        .order_by(Garden.garden_name)
        .all()
    )

    sidebar_gardens = []
    for g in user_gardens:
        zones = sorted(g.robot_zones, key=lambda z: (z.robot_name or "").lower())
        sidebar_gardens.append({"garden": g, "zones": zones})

    # 6) Get sensor config
    cfg = ALERT_CONFIG.get(sensor_type)
    if not cfg:
        abort(404)

    # 7) Get sensor data with period-based filtering
    sensor = Sensor.query.filter_by(
        serial_number=serial_number,
        sensor_type=sensor_type
    ).first()

    if sensor is None:
        abort(404)

    # Get period from query parameter (default: 7 days)
    period = request.args.get('period', '7d')
    
    # Determine cutoff date and format based on period
    today = datetime.utcnow()
    if period == '30d':
        cutoff_date = today - timedelta(days=30)
        time_format = "%d/%m"
    elif period == '3m':
        cutoff_date = today - timedelta(days=90)
        time_format = "%d/%m"
    elif period == '1y':
        cutoff_date = today - timedelta(days=365)
        time_format = "%d/%m"
    else:  # Default: 7d
        cutoff_date = today - timedelta(days=7)
        time_format = "%H:%M"
    
    # Get measurements within the period
    measurements = (
        Measurement.query.filter_by(srnr_sensor=sensor.srnr_sensor)
        .filter(Measurement.time_m >= cutoff_date)
        .order_by(Measurement.time_m.asc())
        .all()
    )

    # Extract values and labels for chart
    chart_values = []
    chart_labels = []
    for m in measurements:
        try:
            chart_values.append(float(m.value))
        except:
            chart_values.append(None)
        if m.time_m:
            chart_labels.append(m.time_m.strftime(time_format))
        else:
            chart_labels.append("")

    # 8) Current measurement & status
    current_measurement = sensor.measurements[0] if sensor.measurements else None
    current_value = float(current_measurement.value) if current_measurement else None

    # 9) Get target values from plant profile
    plant_profile = robot.plant_profile
    target_mean = getattr(plant_profile, cfg["mean_attr"], None) if plant_profile else None
    target_std = getattr(plant_profile, cfg["std_attr"], None) if plant_profile else None

    # 10) Classify status
    severity, status_text, z_score = _classify_status(current_value, target_mean, target_std)

    # 11) Get all measurements for this sensor (extended history for alerts)
    all_measurements = (
        Measurement.query.filter_by(srnr_sensor=sensor.srnr_sensor)
        .order_by(Measurement.time_m.desc())
        .limit(100)
        .all()
    )

    # 12) Build alerts list
    alerts = []
    if severity in ("warning", "critical"):
        if current_value is not None and target_mean is not None:
            direction = "hoger" if current_value > target_mean else "lager"
        else:
            direction = "afwijkend"

        msg = f"{direction.capitalize()} dan ideaal."

        alerts.append({
            "severity": severity,
            "variable": cfg["label"],
            "unit": cfg["unit"],
            "value": round(current_value, 2) if current_value is not None else None,
            "target": (
                f"{target_mean:.1f} ± {target_std:.1f} {cfg['unit']}"
                if target_mean is not None and target_std is not None
                else "n.v.t."
            ),
            "message": msg,
            "z_score": z_score,
            "mean": target_mean,
            "std": target_std,
        })

    # 13) Get tips for this sensor
    tips = cfg.get("tips", [])

    # 14) Statistics
    if chart_values and any(v is not None for v in chart_values):
        valid_values = [v for v in chart_values if v is not None]
        min_value = min(valid_values)
        max_value = max(valid_values)
        avg_value = sum(valid_values) / len(valid_values)
    else:
        min_value = max_value = avg_value = None

    return render_template(
        "sensor_detail.html",
        garden=garden,
        robot=robot,
        sidebar_gardens=sidebar_gardens,
        sensor_type=sensor_type,
        sensor_config=cfg,
        current_value=current_value,
        current_measurement=current_measurement,
        severity=severity,
        status_text=status_text,
        z_score=z_score,
        target_mean=target_mean,
        target_std=target_std,
        chart_values=chart_values,
        chart_labels=chart_labels,
        alerts=alerts,
        tips=tips,
        min_value=min_value,
        max_value=max_value,
        avg_value=avg_value,
        user_name=current_user.uname if current_user else "",
    )


# ====================================================================
# PLANT RECOMMENDATION ENGINE - MOVED TO SEPARATE MODULE
# ====================================================================
# The complete plant recommendation algorithm has been centralized in:
#
#   app/plant_recommendation_engine.py
#
# This module contains:
# - calculate_plant_health_score()     : Core quadratic penalty scoring
# - get_average_measurements()          : Fetch average sensor readings
# - calculate_plant_rankings()          : Rank all plants
# - get_top_recommendations()           : Get top N plants
# - validate_playfield_access()         : Permission checking
# - SENSOR_WEIGHTS                      : Configuration
#
# All functions are imported at the top of this file and used throughout.
# ====================================================================


@dashboard_bp.route("/<serial_number>/plant-recommendation-api", methods=["GET"])
def plant_recommendation_api(serial_number):
    """
    API endpoint: Get plant recommendation for playfield
    
    Query params:
    - days: number of days to analyze (default: 5)
    """
    
    # User authentication
    current_user = _get_current_user()
    if current_user is None:
        return jsonify({"error": "Unauthorized"}), 401
    
    # Playfield validation
    robot = RobotZone.query.filter_by(serial_number=serial_number).first()
    if not robot:
        return jsonify({"error": "Playfield not found"}), 404
    
    # Permission check using centralized function
    if not validate_playfield_access(serial_number, current_user.uemail):
        return jsonify({"error": "Forbidden"}), 403
    
    # Get analysis period
    days = request.args.get("days", 5, type=int)
    days = max(1, min(days, 30))  # Clamp between 1-30
    
    # Get plant rankings using centralized engine
    plant_rankings = calculate_plant_rankings(serial_number, days)
    
    if not plant_rankings:
        return jsonify({
            "error": "No recommendations",
            "message": f"Insufficient measurement data for the last {days} days"
        }), 400
    
    # Get average measurements for the response
    avg_measurements = get_average_measurements(serial_number, days)
    
    # Build response with rankings
    recommendation = {
        "period_days": days,
        "average_measurements": avg_measurements,
        "plant_rankings": [
            {
                "rank": idx + 1,
                "plant_key": plant["key"],
                "display_name": plant["name"],
                "icon": plant["icon"],
                "score": plant["score"],
                "compatibility": plant["compatibility"]
            }
            for idx, plant in enumerate(plant_rankings)
        ],
        "recommended_plant": {
            "rank": 1,
            "plant_key": plant_rankings[0]["key"],
            "display_name": plant_rankings[0]["name"],
            "icon": plant_rankings[0]["icon"],
            "score": plant_rankings[0]["score"],
            "compatibility": plant_rankings[0]["compatibility"]
        }
    }
    
    return jsonify(recommendation)
