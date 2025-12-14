# app/routes/dashboard_routes.py
from math import pi, ceil
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
from ..icons import get_plant_icon
from ..plant_recommendation_engine import (
    calculate_plant_rankings,
    get_top_recommendations,
    get_average_measurements,
    calculate_plant_health_score,
    validate_playfield_access,
    SENSOR_WEIGHTS,
    SENSOR_KEYS as RECOMMENDATION_SENSOR_KEYS,
)
from ..translations import get_translation

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

SENSOR_KEYS = ["moisture", "temperature", "humidity", "rain", "light", "co2"]

# mapping sensor_key -> plant_profile kolommen + labels + tips
ALERT_CONFIG = {
    "moisture": {
        "label": "moisture",
        "unit": "%",
        "mean_attr": "soil_moisture_mean",
        "std_attr": "soil_moisture_std",
        "icon": "💧",
        "tips": [
            "tip_moisture_drip_irrigation",
            "tip_moisture_good_drainage",
            "tip_moisture_increase_watering_dry",
            "tip_moisture_decrease_watering_rain",
            "tip_moisture_soil_compaction",
        ]
    },
    "temperature": {
        "label": "temperature",
        "unit": "°C",
        "mean_attr": "temperature_mean",
        "std_attr": "temperature_std",
        "icon": "🌡️",
        "tips": [
            "tip_temp_adjust_ventilation",
            "tip_temp_increase_heating_cold_night",
            "tip_temp_good_air_circulation",
            "tip_temp_check_greenhouse_insulation",
            "tip_temp_extreme_fluctuations_harm",
        ]
    },
    "humidity": {
        "label": "humidity",
        "unit": "%",
        "mean_attr": "humidity_mean",
        "std_attr": "humidity_std",
        "icon": "💨",
        "tips": [
            "tip_humidity_increase_misting",
            "tip_humidity_improve_ventilation_high",
            "tip_humidity_diseases_thrive_high",
            "tip_humidity_low_hinders_growth",
            "tip_humidity_check_hvac",
        ]
    },
    "rain": {
        "label": "rain",
        "unit": "mm/week",
        "mean_attr": "rain_mm_week_mean",
        "std_attr": "rain_mm_week_std",
        "icon": "🌧️",
        "tips": [
            "tip_rain_adjust_irrigation_natural",
            "tip_rain_use_rainwater_harvesting",
            "tip_rain_check_drainage_heavy_rain",
            "tip_rain_prevent_stagnation_root_rot",
            "tip_rain_monitor_weather_irrigation",
        ]
    },
    "light": {
        "label": "light",
        "unit": "µmol/m²/s",
        "mean_attr": "ppfd_mean",
        "std_attr": "ppfd_std",
        "icon": "☀️",
        "tips": [
            "tip_light_increase_intensity_grow_lights",
            "tip_light_ppfd_more_important_duration",
            "tip_light_check_led_height",
            "tip_light_clean_reflectors_optimal_output",
            "tip_light_seasonal_change_natural_light",
        ]
    },
    "co2": {
        "label": "co2",
        "unit": "ppm",
        "mean_attr": "co2_mean",
        "std_attr": "co2_std",
        "icon": "🌿",
        "tips": [
            "tip_co2_low_growth_limitation",
            "tip_co2_optimal_range",
            "tip_co2_improve_ventilation_supplement",
            "tip_co2_sources",
            "tip_co2_high_negative_without_light",
        ]
    },
}



def _get_current_user():
    user_email = session.get("user_email")
    if not user_email:
        return None
    return User.query.filter_by(uemail=user_email).first()

def _resolve_lang():
    lang = request.args.get("lang")
    if not lang:
        lang = session.get("lang")
    if not lang:
        lang = request.accept_languages.best_match(["nl", "en"])
    return lang or "nl"


def _get_or_create_daily_health_score(robot, sensor_data):
    """
    Get existing health score for the measurement date, or create one if it doesn't exist.
    The health score date must match the date of the measurements used to calculate it.
    Ensures at most 1 score per playfield per measurement date (idempotent).
    
    Algorithm:
    1. Bepaal de datum van de LAATSTE meting
    2. Controleer of er al een score voor DIE DAG bestaat
    3. Zo ja: return bestaande score (idempotent)
    4. Zo nee: bereken score en sla op MET DE DATUM VAN DE METING (niet huiding datum)
    
    Returns: HealthScore object (either existing or newly created), or None
    """
    serial_number = robot.serial_number
    
    # 1) Bepaal de datum van de LAATSTE meting
    # Zoek de meest recente meting op alle sensoren
    measurement_date = None
    for key in SENSOR_KEYS:
        meas = sensor_data[key]["measurement"]
        if meas is not None and meas.time_m is not None:
            meas_date = meas.time_m.date()
            if measurement_date is None or meas_date > measurement_date:
                measurement_date = meas_date
    
    if measurement_date is None:
        # Geen metingen beschikbaar
        return None
    
    # 2) Controleer of score al bestaat voor DEZE DAG
    # Eerst proberen via score_date (nieuwe kolom)
    existing_score = HealthScore.query.filter(
        HealthScore.serial_number == serial_number,
        HealthScore.score_date == measurement_date
    ).first()
    
    # Fallback: als score_date nog niet bestaat in database, zoeken via calculated_at
    if existing_score is None:
        try:
            existing_score = HealthScore.query.filter(
                HealthScore.serial_number == serial_number,
                func.date(HealthScore.calculated_at) == measurement_date
            ).first()
        except Exception:
            pass
    
    # 3) Als score al bestaat: return hem (idempotent)
    if existing_score:
        return existing_score
    
    # 4) Score bestaat niet: bereken hem
    calculated_health_score = _calculate_daily_health_score(robot, sensor_data)
    
    if calculated_health_score is None:
        return None
    
    # Set calculated_at to the measurement date at midnight
    # (Dit is de datum van de meting, NIET de huidige datum)
    calculated_at = datetime.combine(measurement_date, datetime.min.time())
    
    # Try to insert new score
    try:
        new_health_score = HealthScore(
            serial_number=serial_number,
            score=calculated_health_score,
            score_date=measurement_date,  # BELANGRIJK: opslaan met METING-datum
            calculated_at=calculated_at,
        )
        db.session.add(new_health_score)
        db.session.commit()
        return new_health_score
    except Exception as e:
        # Race condition: request voegde al een score toe voor deze dag
        # Rollback en fetch de bestaande
        db.session.rollback()
        existing_score = HealthScore.query.filter(
            HealthScore.serial_number == serial_number,
            HealthScore.score_date == measurement_date
        ).first()
        
        # Fallback
        if existing_score is None:
            try:
                existing_score = HealthScore.query.filter(
                    HealthScore.serial_number == serial_number,
                    func.date(HealthScore.calculated_at) == measurement_date
                ).first()
            except Exception:
                pass
        
        return existing_score

def _classify_status(value, mean, std, lang="nl"):
    """
    Geeft (severity, status_text, z-score) terug.
    severity: 'ok', 'warning', 'critical', 'unknown'
    """
    if value is None or mean is None or std is None:
        return "unknown", get_translation("no_data", lang), None

    try:
        v = float(value)
        m = float(mean)
        s = float(std)
    except Exception:
        return "unknown", get_translation("no_data", lang), None

    if s == 0:
        return "unknown", get_translation("no_reference", lang), None

    z = abs((v - m) / s)

    if z < 1:
        return "ok", get_translation("optimal", lang), z
    elif z < 2:
        return "warning", get_translation("slight_deviation", lang), z
    else:
        return "critical", get_translation("strong_deviation", lang), z

def _get_translated_tips(sensor_type, lang):
    """
    Haalt de tips voor een specifieke sensortype op en vertaalt ze.
    """
    cfg = ALERT_CONFIG.get(sensor_type)
    if not cfg or "tips" not in cfg:
        return []
    
    translated_tips = [get_translation(tip_key, lang) for tip_key in cfg["tips"]]
    return translated_tips


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
        float: Quality score 0-100, or 0 if invalid data (always returns a number, never None)
    """
    if value is None or mean is None or std is None:
        return 0  # Return 0 instead of None for invalid data
    
    try:
        v = float(value)
        m = float(mean)
        s = float(std)
    except Exception:
        return 0  # Return 0 instead of None
    
    if s == 0:
        return 0  # Return 0 instead of None for zero standard deviation
    
    # Calculate deviation in standard deviations
    x = abs((v - m) / s)
    
    # Apply quadratic penalty: score = max(0, 1 - x²) × 100
    quality = max(0, 1 - (x ** 2)) * 100
    return round(quality, 1)

def _calculate_daily_health_score(robot, sensor_data):
    """
    Berekent de dagelijkse gezondheidsscore met DEZELFDE formule als calculate_plant_health_score.
    Dit zorgt ervoor dat de dashboard score EXACT hetzelfde is als de recommended plants scores.
    
    Gebruikt get_average_measurements (gemiddelde van afgelopen 5 dagen) zodat beide scores identiek zijn.
    
    HealthScore = (sum(w_v * max(0, 1 - (|m_v - opt_v| / dev_v)^2)) / sum(w_v)) * 100
    
    Returns: float (0-100) of None als onvoldoende data
    """
    plant_profile = robot.plant_profile
    if plant_profile is None:
        return None
    
    # Converteer ORM object naar dict (exact zoals in calculate_plant_health_score)
    plant_data = {
        'moisture_mean': plant_profile.soil_moisture_mean,
        'moisture_std': plant_profile.soil_moisture_std,
        'temperature_mean': plant_profile.temperature_mean,
        'temperature_std': plant_profile.temperature_std,
        'humidity_mean': plant_profile.humidity_mean,
        'humidity_std': plant_profile.humidity_std,
        'rain_mean': plant_profile.rain_mm_week_mean,
        'rain_std': plant_profile.rain_mm_week_std,
        'light_mean': plant_profile.ppfd_mean,
        'light_std': plant_profile.ppfd_std,
        'co2_mean': plant_profile.co2_mean,
        'co2_std': plant_profile.co2_std,
    }
    
    # Gebruik AVERAGE measurements (exact zoals calculate_plant_rankings doet)
    # Dit zorgt ervoor dat dashboard en recommended plants dezelfde input hebben
    measurements = get_average_measurements(robot.serial_number, days=5)
    
    # Gebruik exact dezelfde algoritme als calculate_plant_health_score
    score = calculate_plant_health_score(measurements, plant_data)
    
    return score


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
        period_label = "Laatste 7 dagen"
        fmt = "%d/%m"  # Day/Month
        desired_ticks = 7
    elif period == 'month':
        days = 30
        period_label = "Laatste 30 dagen"
        fmt = "%d/%m"  # Day/Month
        desired_ticks = 5  # ongeveer elke 6 dagen
    elif period == 'quarter':
        days = 90
        period_label = "Laatste 3 maanden"
        fmt = "%d %b"  # Dag + maandkort
        desired_ticks = 3  # 1 per maand
    elif period == 'year':
        days = 365
        period_label = "Afgelopen jaar"
        fmt = "%b %y"  # Wordt overschreven voor labeling met dag (1 May 25)
        desired_ticks = 4  # 1 per kwartaal
    else:
        days = 30
        period_label = "Laatste 30 dagen"
        fmt = "%d/%m"
        desired_ticks = 7
    
    # Haal huidige periode op
    start_date = today - timedelta(days=days)
    current_scores = (
        HealthScore.query.filter_by(serial_number=serial_number)
        .filter(HealthScore.calculated_at >= datetime.combine(start_date, datetime.min.time()))
        .filter(HealthScore.calculated_at <= datetime.combine(today, datetime.max.time()))
        .order_by(HealthScore.calculated_at.asc())
        .all()
    )
    
    # Formatteer data voor grafiek met intelligente label spacing
    values = [float(s.score) for s in current_scores]
    all_dates = [s.calculated_at.date() for s in current_scores if s.calculated_at]

    labels = []
    if all_dates:
        first_date = all_dates[0]
        last_idx = len(all_dates) - 1

        for i, dt in enumerate(all_dates):
            add_label = False

            if period == 'week':
                add_label = True  # alle 7 dagen tonen
            elif period == 'month':
                add_label = ((dt - first_date).days % 7 == 0) or (i == last_idx)
            elif period == 'quarter':
                add_label = ((dt - first_date).days % 14 == 0) or (i == last_idx)
            elif period == 'year':
                add_label = (dt.day == 1 and dt.month in (1, 3, 5, 7, 9, 11)) or (i == last_idx)
            else:
                add_label = ((dt - first_date).days % 7 == 0) or (i == last_idx)

            if add_label:
                if period == 'year':
                    # Toon "1 May 25" etc. voor eerste dag van de geselecteerde maanden
                    label = dt.strftime("%d %b %y").lstrip("0")
                else:
                    label = dt.strftime(fmt)
                labels.append(label)
            else:
                labels.append("")

    # Start/nu voor deze grafiek (eerste en laatste datapunt)
    start_score = round(values[0], 1) if values else 0
    end_score = round(values[-1], 1) if values else 0

    # Bereken trend percentage t.o.v. eerste zichtbare datapunt
    if values and start_score != 0:
        change = ((end_score - start_score) / start_score) * 100
        trend_direction = "up" if change > 0 else "down" if change < 0 else "neutral"
        trend_percent = abs(round(change, 1))
    else:
        trend_percent = 0
        trend_direction = "neutral"
    
    return {
        'values': values,
        'labels': labels,
        'trend_percent': abs(trend_percent),
        'trend_direction': trend_direction,
        'period_label': period_label,
        'current_avg': end_score,
        'previous_avg': start_score,
        'start_score': start_score,
        'end_score': end_score,
    }


@dashboard_bp.route("/<serial_number>")
def dashboard(serial_number):
    # 0) Resolve language
    lang = _resolve_lang()

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
        optimal_mean_weekly = None
        optimal_std_weekly = None
        if plant_profile and cfg:
            optimal_mean = getattr(plant_profile, cfg["mean_attr"], None)
            optimal_std = getattr(plant_profile, cfg["std_attr"], None)
            # For rain: store both weekly and daily optimal values
            if key == "rain" and optimal_mean is not None and optimal_std is not None:
                optimal_mean_weekly = float(optimal_mean)
                optimal_std_weekly = float(optimal_std)
                optimal_mean = optimal_mean_weekly / 7.0
                optimal_std = optimal_std_weekly / 7.0

        sensor_data[key] = {
            "sensor": sensor,
            "measurement": measurement,
            "series": series,
            "values": values,
            "labels": labels,
            "optimal_mean": optimal_mean,
            "optimal_std": optimal_std,
            "optimal_mean_weekly": optimal_mean_weekly,
            "optimal_std_weekly": optimal_std_weekly,
        }

    # 5) Alerts & factor status op basis van PlantProfile
    alerts = []
    factor_states = {}

    for key in SENSOR_KEYS:
        cfg = ALERT_CONFIG.get(key)
        meas = sensor_data[key]["measurement"]
        
        # For rain: use sum of last 7 daily measurements (weekly total)
        if key == "rain":
            sensor = (
                Sensor.query.filter_by(serial_number=serial_number, sensor_type=key)
                .first()
            )
            if sensor:
                rain_measurements = (
                    Measurement.query.filter_by(srnr_sensor=sensor.srnr_sensor)
                    .order_by(Measurement.time_m.desc())
                    .limit(7)
                    .all()
                )
                value = sum(float(m.value) if m.value else 0 for m in rain_measurements) if rain_measurements else None
            else:
                value = None
        else:
            value = float(meas.value) if meas is not None else None

        mean = getattr(plant_profile, cfg["mean_attr"], None) if plant_profile else None
        std = getattr(plant_profile, cfg["std_attr"], None) if plant_profile else None

        severity, status_text, z = _classify_status(value, mean, std, lang)
        quality_score = _calculate_quality_score(value, mean, std)
        
        # Bereken invulling percentage voor gecentreerde balk
        # Balk loopt van 0 tot 2*mean, met mean in het midden (50%)
        # invulling = (value / (2 * mean)) * 100
        if value is not None and mean is not None and mean > 0:
            invulling_percentage = (float(value) / (2 * float(mean))) * 100
            # Clip tussen 0-100% voor visuele weergave
            invulling_percentage = max(0, min(100, invulling_percentage))
        else:
            invulling_percentage = 50  # Default naar midden als geen data
        
        # Bereken deviation (aantal standaardafwijkingen) voor kleuring
        if value is not None and mean is not None and std is not None and std > 0:
            deviation = abs(float(value) - float(mean)) / float(std)
        else:
            deviation = None

        factor_states[key] = {
            "severity": severity,
            "status_text": status_text,
            "z": z,
            "mean": mean,
            "std": std,
            "value": value,
            "quality_score": quality_score,
            "invulling_percentage": invulling_percentage,
            "deviation": deviation,  # aantal σ
        }

        if severity in ("warning", "critical"):
            if value is not None and mean is not None:
                direction = "higher" if value > mean else "lower"
            else:
                direction = "deviating"

            if direction == "higher":
                msg = get_translation("higher_than_ideal", lang)
            elif direction == "lower":
                msg = get_translation("lower_than_ideal", lang)
            else:
                msg = get_translation("deviating_from_ideal", lang)

            alerts.append(
                {
                    "severity": severity,
                    "variable": get_translation(key, lang),
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

    # 5.5) ALTIJD health score berekenen op basis van huidige plant_profile
    # Dit zorgt ervoor dat als je een andere plant kiest, de score meteen verandert
    calculated_health_score = _calculate_daily_health_score(robot, sensor_data)

    # 6) Health score uit berekening (niet uit database)
    if calculated_health_score is not None:
        health_score = int(calculated_health_score)
    else:
        health_score = 0
    
    # Sla ook op in database voor historische data (maar laat niet de view blokkeren)
    try:
        _get_or_create_daily_health_score(robot, sensor_data)
    except:
        pass  # Negeer database fouten, we hebben al de berekende score

    if health_score >= 90:
        health_label = get_translation("excellent_growth_conditions", lang)
    elif health_score >= 70:
        health_label = get_translation("good_growth_conditions", lang)
    elif health_score >= 50:
        health_label = get_translation("fair_growth_conditions", lang)
    else:
        health_label = get_translation("attention_required", lang)

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
                        'key': plant.plant_name,
                        'name': plant.display_name,
                        'icon': get_plant_icon(plant.plant_name),
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
    # 0) Resolve language
    lang = _resolve_lang()

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
    
    # Determine number of measurements and time format based on sensor type and period
    # Default behavior: 24 measurements for most sensors, 7 for rain and light
    if period == '30d':
        num_measurements = 30
        time_format = "%d/%m"
    elif period == '3m':
        num_measurements = 90
        time_format = "%d/%m"
    elif period == '1y':
        num_measurements = 365
        time_format = "%d/%m"
    else:  # Default: use sensor type to determine
        if sensor_type in ['rain', 'light']:
            num_measurements = 7
            time_format = "%d/%m"  # Show dates for rain and light
        else:
            num_measurements = 24
            time_format = "%H:%M"  # Show times for other sensors
    
    # Get the last N measurements ordered ascending (oldest to newest for chart display)
    measurements = (
        Measurement.query.filter_by(srnr_sensor=sensor.srnr_sensor)
        .order_by(Measurement.time_m.desc())
        .limit(num_measurements)
        .all()
    )
    # Reverse to ascending order for chart display
    measurements = list(reversed(measurements))

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

    # 8) Current measurement & status - Get the LATEST measurement (most recent)
    current_measurement = (
        Measurement.query.filter_by(srnr_sensor=sensor.srnr_sensor)
        .order_by(Measurement.time_m.desc())
        .first()
    ) if sensor else None
    current_value = float(current_measurement.value) if current_measurement else None

    # 9) Get target values from plant profile
    plant_profile = robot.plant_profile
    target_mean = getattr(plant_profile, cfg["mean_attr"], None) if plant_profile else None
    target_std = getattr(plant_profile, cfg["std_attr"], None) if plant_profile else None

    # 10) Classify status
    severity, status_text, z_score = _classify_status(current_value, target_mean, target_std, lang)

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
        # For rain alerts, compare weekly total against ideal (weekly) mean
        if sensor_type == "rain" and target_mean is not None:
            rain_total = sum(v for v in chart_values if v is not None)
            direction_key = "higher_than_ideal" if rain_total > target_mean else "lower_than_ideal"
        elif current_value is not None and target_mean is not None:
            direction_key = "higher_than_ideal" if current_value > target_mean else "lower_than_ideal"
        else:
            direction_key = "lower_than_ideal"

        msg = get_translation(direction_key, lang)

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

    # 12b) Build factor_states for all sensors
    factor_states = {}
    for key in SENSOR_KEYS:
        sensor_cfg = ALERT_CONFIG.get(key)
        sensor_obj = Sensor.query.filter_by(
            serial_number=serial_number,
            sensor_type=key
        ).first()
        
        if sensor_obj is not None and sensor_obj.measurements:
            meas_val = float(sensor_obj.measurements[0].value)
        else:
            meas_val = None
        
        mean = getattr(plant_profile, sensor_cfg["mean_attr"], None) if plant_profile else None
        std = getattr(plant_profile, sensor_cfg["std_attr"], None) if plant_profile else None
        
        sev, stat_txt, z = _classify_status(meas_val, mean, std, lang)
        
        factor_states[key] = {
            "severity": sev,
            "status_text": stat_txt,
            "z": z,
            "mean": mean,
            "std": std,
            "current_value": meas_val,
        }

    # 13) Get tips for this sensor
    tips = _get_translated_tips(sensor_type, lang)

    # 14) Statistics
    if chart_values and any(v is not None for v in chart_values):
        valid_values = [v for v in chart_values if v is not None]
        min_value = min(valid_values)
        max_value = max(valid_values)
        
        # For rain: total (sum) instead of average
        if sensor_type == "rain":
            avg_value = sum(valid_values)
            stat_type = "total"
        else:
            avg_value = sum(valid_values) / len(valid_values)
            stat_type = "average"
    else:
        min_value = max_value = avg_value = None
        stat_type = "average"

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
        factor_states=factor_states,
        tips=tips,
        min_value=min_value,
        max_value=max_value,
        avg_value=avg_value,
        stat_type=stat_type,
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
