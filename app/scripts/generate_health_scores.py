#!/usr/bin/env python3
"""
Generate health scores for a playfield based on recent measurements

Usage:
    python3 -m app.scripts.generate_health_scores --playfield RZ-001-A --days 5
"""

import sys
import os
from datetime import datetime, timedelta, date
from argparse import ArgumentParser

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app import create_app, db
from app.models import RobotZone, Sensor, Measurement, HealthScore

app = create_app()

SENSOR_KEYS = ["moisture", "temperature", "humidity", "rain", "light", "co2"]

SENSOR_WEIGHTS = {
    "moisture": 0.25,
    "temperature": 0.20,
    "humidity": 0.15,
    "rain": 0.15,
    "light": 0.15,
    "co2": 0.10,
}


def calculate_daily_health_score(serial_number, score_date):
    """
    Berekent gezondheidscore voor een specifieke dag
    """
    
    # Get plant profile
    robot = RobotZone.query.filter_by(serial_number=serial_number).first()
    if not robot or not robot.plant_profile:
        print(f"  ❌ No plant profile for {serial_number}")
        return None
    
    plant_profile = robot.plant_profile
    
    # Date range for this day
    start_of_day = datetime.combine(score_date, datetime.min.time())
    end_of_day = datetime.combine(score_date, datetime.max.time())
    
    # Calculate average per sensor for this day
    measurements_dict = {}
    for sensor_type in SENSOR_KEYS:
        sensor = Sensor.query.filter_by(
            serial_number=serial_number,
            sensor_type=sensor_type
        ).first()
        
        if not sensor:
            continue
        
        # Average value for this day
        avg_value = db.session.query(
            db.func.avg(Measurement.value)
        ).filter(
            Measurement.srnr_sensor == sensor.srnr_sensor,
            Measurement.time_m >= start_of_day,
            Measurement.time_m <= end_of_day
        ).scalar()
        
        if avg_value is not None:
            measurements_dict[sensor_type] = float(avg_value)
    
    if not measurements_dict:
        return None
    
    # Calculate health score using quadratic formula
    weighted_sum = 0
    weights_sum = 0
    
    for sensor_type, weight in SENSOR_WEIGHTS.items():
        measurement = measurements_dict.get(sensor_type)
        
        if measurement is None:
            continue
        
        # Get optimal values from plant profile
        if sensor_type == "moisture":
            opt_mean = plant_profile.soil_moisture_mean
            opt_std = plant_profile.soil_moisture_std
        elif sensor_type == "temperature":
            opt_mean = plant_profile.temperature_mean
            opt_std = plant_profile.temperature_std
        elif sensor_type == "humidity":
            opt_mean = plant_profile.humidity_mean
            opt_std = plant_profile.humidity_std
        elif sensor_type == "rain":
            opt_mean = plant_profile.rain_mm_week_mean
            opt_std = plant_profile.rain_mm_week_std
        elif sensor_type == "light":
            opt_mean = plant_profile.ppfd_mean
            opt_std = plant_profile.ppfd_std
        elif sensor_type == "co2":
            opt_mean = plant_profile.co2_mean
            opt_std = plant_profile.co2_std
        else:
            continue
        
        if opt_mean is None or opt_std is None:
            continue
        
        # Quadratic scoring: s_v = max(0, 1 - (|m_v - opt_v| / dev_v)²)
        try:
            deviation = abs(float(measurement) - float(opt_mean)) / float(opt_std)
            sensor_score = max(0, 1 - (deviation ** 2))
            weighted_sum += sensor_score * weight
            weights_sum += weight
        except (ValueError, ZeroDivisionError):
            continue
    
    if weights_sum == 0:
        return None
    
    # Normalize to 0-100
    health_score = (weighted_sum / weights_sum) * 100
    return round(health_score, 2)


def generate_health_scores(playfield_serial, days=5):
    """
    Genereert gezondheidsscores voor de afgelopen N dagen
    """
    
    robot = RobotZone.query.filter_by(serial_number=playfield_serial).first()
    if not robot:
        print(f"❌ Playfield {playfield_serial} not found")
        return False
    
    if not robot.plant_profile:
        print(f"❌ No plant profile for {playfield_serial}")
        return False
    
    now = datetime.utcnow()
    scores_created = 0
    
    for day_offset in range(days):
        score_date = (now - timedelta(days=day_offset)).date()
        
        # Check if score already exists
        existing = HealthScore.query.filter_by(
            serial_number=playfield_serial,
            score_date=score_date
        ).first()
        
        if existing:
            print(f"  ⊙ {score_date}: Already exists (score={existing.score})")
            continue
        
        # Calculate score
        score = calculate_daily_health_score(playfield_serial, score_date)
        
        if score is not None:
            health_score_record = HealthScore(
                score=score,
                score_date=score_date,
                calculated_at=datetime.utcnow(),
                serial_number=playfield_serial
            )
            db.session.add(health_score_record)
            print(f"  ✓ {score_date}: Score={score:.2f}")
            scores_created += 1
        else:
            print(f"  ✗ {score_date}: Could not calculate (no data)")
    
    db.session.commit()
    return scores_created > 0


def main():
    parser = ArgumentParser(description="Generate health scores for playfield")
    parser.add_argument("--playfield", "-p", required=True, help="Playfield serial number (e.g., RZ-001-A)")
    parser.add_argument("--days", "-d", type=int, default=5, help="Number of days to generate (default: 5)")
    
    args = parser.parse_args()
    
    with app.app_context():
        print("=" * 60)
        print("🏥 Health Score Generator")
        print("=" * 60)
        
        print(f"\n📍 Playfield: {args.playfield}")
        print(f"📅 Days: {args.days}")
        
        print("\n🔄 Generating health scores...")
        if generate_health_scores(args.playfield, args.days):
            print(f"\n✅ Successfully generated health scores")
            print("\nYou can now view plant recommendations on the dashboard!")
        else:
            print("\n❌ Failed to generate health scores")
            sys.exit(1)


if __name__ == "__main__":
    main()
