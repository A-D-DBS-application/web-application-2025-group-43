"""
PLANT RECOMMENDATION ENGINE
====================================================================
Complete algorithm for calculating plant health scores and recommendations
based on sensor measurements and plant profiles.

Author: Capenta Development Team
Date: December 2025

ALGORITHM OVERVIEW:
-------------------
The engine calculates suitability scores for all available plants based on
current environmental conditions. Each plant has optimal parameter ranges
(mean ± std) for 6 sensor types. The algorithm:

1. Collects average sensor measurements from the last N days
2. For each plant profile, calculates a quadratic penalty score
3. Weighs each sensor type according to importance
4. Returns normalized 0-100 score for each plant
5. Ranks plants by score and returns top recommendations

MATHEMATICAL FORMULA:
-------------------
For each sensor measurement:
    x_v = |measurement_v - optimal_mean_v| / optimal_std_v
    s_v = max(0, 1 - x_v²)  [quadratic penalty function]

Final score = (Σ(w_v × s_v)) / Σ(w_v) × 100

Where:
    w_v = weight for sensor v (sum = 1.0)
    s_v = normalized score for sensor v
    x_v = deviation (in standard deviations) from optimal
"""

from datetime import datetime, timedelta
import math
from app import db
from app.models import Sensor, Measurement, PlantProfile, RobotZone
from sqlalchemy import func


# ====================================================================
# CONFIGURATION: SENSOR WEIGHTS AND KEYS
# ====================================================================
"""
Sensor importance weights - sum to 1.0
Adjusted based on typical indoor farming priority:
- Soil moisture: 25% (critical for plant health)
- Temperature: 20% (affects all biochemical processes)
- Humidity: 15% (affects transpiration and photosynthesis)
- Rainfall/Water: 15% (waterbehoefte/irrigation)
- Light: 15% (essential for photosynthesis)
- CO₂: 10% (supporting factor for growth)
"""
SENSOR_WEIGHTS = {
    "moisture": 0.25,      # 25% - zeer belangrijk
    "temperature": 0.20,   # 20% - belangrijk
    "humidity": 0.15,      # 15% - belangrijk
    "rain": 0.15,          # 15% - waterbehoefte
    "light": 0.15,         # 15% - fotosynthese
    "co2": 0.10,           # 10% - ondersteunend
}

# Sensor type keys matching database and SENSOR_WEIGHTS
SENSOR_KEYS = list(SENSOR_WEIGHTS.keys())


# ====================================================================
# CORE ALGORITHM FUNCTIONS
# ====================================================================

def calculate_plant_health_score(measurements_dict, plant_profile):
    """
    Calculate suitability score for a specific plant based on current measurements.
    
    This is the CORE ALGORITHM - implements the Gaussian penalty scoring method.
    
    Args:
        measurements_dict (dict): Current average sensor measurements
            Format: {"moisture": 45.2, "temperature": 23.1, ...}
        plant_profile (dict): Plant profile with means and stds
            Format: {
                "moisture_mean": 50, "moisture_std": 5,
                "temperature_mean": 22, "temperature_std": 2,
                ...
            }
    
    Returns:
        float: Normalized score 0-100, or None if insufficient data
        
    Algorithm Steps:
    ----------------
    1. For each sensor type:
        - Get measurement and plant's optimal (mean, std)
        - Calculate deviation: x_v = |measurement - mean| / std
        - Apply Gaussian penalty: s_v = exp(-(x_v² / 2))
        
    2. Calculate weighted average:
        final_score = (Σ weighted_scores) / (Σ weights) × 100
        
    3. Return rounded score (0-100)
    
    Example:
    --------
    If plant wants 50% moisture ±5%, and we have 52.5%:
        deviation = |52.5 - 50| / 5 = 0.5
        score = exp(-(0.5²/2)) = exp(-0.125) = 0.88 (88% for this sensor)
        
    If we have 60% (way off):
        deviation = |60 - 50| / 5 = 2.0
        score = exp(-(2.0²/2)) = exp(-2) = 0.135 (13.5% - still penalized but more forgiving)
    """
    
    if not measurements_dict or not plant_profile:
        return None
    
    weighted_sum = 0
    weights_sum = 0
    
    # Process each sensor type
    for sensor_type, weight in SENSOR_WEIGHTS.items():
        measurement = measurements_dict.get(sensor_type)
        
        # Skip if no measurement available
        if measurement is None:
            continue
        
        # Get plant's optimal values (mean ± std)
        attr_mean = plant_profile.get(f"{sensor_type}_mean")
        attr_std = plant_profile.get(f"{sensor_type}_std")
        
        # Skip if plant profile incomplete for this sensor
        if attr_mean is None or attr_std is None:
            continue
        
        # Calculate Gaussian penalty score
        try:
            # Step 1: Calculate deviation in standard deviations
            deviation = abs(float(measurement) - float(attr_mean)) / float(attr_std)
            
            # Step 2: Apply Gaussian penalty function (normal distribution bell curve)
            # Uses bell curve (normal distribution) for forgiving scoring
            # Interpretation:
            # - deviation 0-0.5: excellent (score 88-100%)
            # - deviation 0.5-1.0: good (score 61-88%)
            # - deviation 1.0-1.5: acceptable (score 32-61%)
            # - deviation 1.5-2.0: poor (score 14-32%)
            # - deviation >2.0: very poor (<14%)
            sensor_score = math.exp(-(deviation ** 2) / 2)
            
            # Step 3: Add weighted contribution
            weighted_sum += sensor_score * weight
            weights_sum += weight
            
        except (ValueError, ZeroDivisionError):
            # Skip if conversion or division fails
            continue
    
    # No valid sensors processed
    if weights_sum == 0:
        return None
    
    # Normalize to 0-100 scale
    final_score = (weighted_sum / weights_sum) * 100
    return round(final_score, 2)


def get_average_measurements(serial_number, days=5):
    """
    Retrieve average sensor measurements for the last N days.
    
    Special handling for rain: sums last 7 daily measurements (weekly total)
    instead of averaging, since rain optimal is weekly-based.
    
    Since physical sensors may not take measurements daily, this function
    falls back to using the latest available measurements if no data exists
    within the specified time window.
    
    Args:
        serial_number (str): Serial number of the robot/playfield
        days (int): Number of days to look back (default: 5)
    
    Returns:
        dict: Average measurements by sensor type
            Format: {
                "moisture": 45.2,
                "temperature": 23.1,
                "humidity": 65.3,
                "rain": 32.5,  (weekly total sum)
                "light": 450.2,
                "co2": 520.1
            }
    """
    
    measurements_avg = {}
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    for sensor_type in SENSOR_KEYS:
        # Find sensor for this robot
        sensor = Sensor.query.filter_by(
            serial_number=serial_number,
            sensor_type=sensor_type
        ).first()
        
        if not sensor:
            measurements_avg[sensor_type] = None
            continue
        
        # Special handling for rain: sum last 7 daily measurements (weekly total)
        if sensor_type == "rain":
            rain_cutoff = datetime.utcnow() - timedelta(days=7)
            rain_measurements = Measurement.query.filter(
                Measurement.srnr_sensor == sensor.srnr_sensor,
                Measurement.time_m >= rain_cutoff
            ).all()
            
            if rain_measurements:
                total_rain = sum(float(m.value) if m.value else 0 for m in rain_measurements)
                measurements_avg[sensor_type] = total_rain
            else:
                # Fallback: get latest measurement
                latest = Measurement.query.filter_by(
                    srnr_sensor=sensor.srnr_sensor
                ).order_by(Measurement.time_m.desc()).first()
                measurements_avg[sensor_type] = float(latest.value) if latest and latest.value else None
        else:
            # For other sensors: calculate average within the time window
            avg_value = db.session.query(
                func.avg(Measurement.value)
            ).filter(
                Measurement.srnr_sensor == sensor.srnr_sensor,
                Measurement.time_m >= cutoff_date
            ).scalar()
            
            # If no data within the time window, use the latest measurement
            if avg_value is None:
                latest_measurement = (
                    Measurement.query.filter_by(srnr_sensor=sensor.srnr_sensor)
                    .order_by(Measurement.time_m.desc())
                    .first()
                )
                avg_value = latest_measurement.value if latest_measurement else None
            
            measurements_avg[sensor_type] = float(avg_value) if avg_value else None
    
    return measurements_avg


def calculate_plant_rankings(serial_number, days=5):
    """
    Calculate plant suitability scores and return ranked list.
    
    This function orchestrates the full recommendation process:
    1. Gets average measurements for the playfield
    2. Scores all plants in the database
    3. Sorts by score descending
    
    Args:
        serial_number (str): Serial number of the robot/playfield
        days (int): Number of days to analyze (default: 5)
    
    Returns:
        list: Sorted list of plants with scores
            Format: [
                {
                    'key': 'basil',
                    'name': 'Basil',
                    'score': 85.5,
                    'compatibility': 'Excellent'
                },
                ...
            ]
            Or empty list if insufficient data
    """
    
    # Get current measurements
    avg_measurements = get_average_measurements(serial_number, days)
    
    # Check if we have any data
    if not any(v is not None for v in avg_measurements.values()):
        return []
    
    # Score all plants
    plant_rankings = []
    all_plants = PlantProfile.query.all()
    
    for plant in all_plants:
        # Convert PlantProfile ORM object to dict
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
        
        # Calculate score for this plant
        score = calculate_plant_health_score(avg_measurements, plant_data)
        
        if score is not None:
            # Classify compatibility
            if score >= 80:
                compatibility = "Excellent"
            elif score >= 60:
                compatibility = "Good"
            elif score >= 40:
                compatibility = "Fair"
            else:
                compatibility = "Poor"
            
            plant_rankings.append({
                'key': plant.plant_name,
                'name': plant.display_name,
                'icon': '🌱',
                'score': round(score, 2),
                'compatibility': compatibility
            })
    
    # Sort by score descending
    plant_rankings.sort(key=lambda x: x['score'], reverse=True)
    
    return plant_rankings


def get_top_recommendations(serial_number, top_n=3, days=5):
    """
    Get the top N recommended plants for a playfield.
    
    Convenience function - wrapper around calculate_plant_rankings
    that returns only the top N results.
    
    Args:
        serial_number (str): Serial number of the robot/playfield
        top_n (int): Number of top recommendations to return (default: 3)
        days (int): Number of days to analyze (default: 5)
    
    Returns:
        list: Top N plants by score
    """
    
    rankings = calculate_plant_rankings(serial_number, days)
    return rankings[:top_n] if rankings else []


# ====================================================================
# UTILITY FUNCTIONS
# ====================================================================

def validate_playfield_access(serial_number, user_email):
    """
    Validate that a user has permission to access a playfield.
    
    Args:
        serial_number (str): Serial number of the playfield
        user_email (str): Email of the user to check
    
    Returns:
        bool: True if user has access, False otherwise
    """
    
    robot = RobotZone.query.filter_by(serial_number=serial_number).first()
    if not robot:
        return False
    
    return robot.garden.user_email == user_email


def get_recommendation_confidence(score):
    """
    Get a confidence level based on score.
    
    Args:
        score (float): Plant score (0-100)
    
    Returns:
        str: Confidence level
    """
    
    if score >= 90:
        return "Very High"
    elif score >= 75:
        return "High"
    elif score >= 60:
        return "Medium"
    elif score >= 40:
        return "Low"
    else:
        return "Very Low"
