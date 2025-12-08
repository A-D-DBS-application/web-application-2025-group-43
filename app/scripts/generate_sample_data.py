#!/usr/bin/env python3
"""
Generate sample sensor data for testing plant recommendations

Usage:
    python3 -m app.scripts.generate_sample_data --playfield RZ-001 --days 5
"""

import sys
import os
import random
import math
from datetime import datetime, timedelta
from argparse import ArgumentParser

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app import create_app, db
from app.models import RobotZone, Sensor, Measurement

app = create_app()

SENSOR_TYPES = ["moisture", "temperature", "humidity", "rain", "light", "co2"]

# Base realistic values
BASE_VALUES = {
    "moisture": 65,      # %
    "temperature": 20,   # °C
    "humidity": 70,      # %
    "rain": 50,          # mm/week (dagelijks: ~7mm)
    "light": 400,        # PPFD µmol/m²/s
    "co2": 600,          # ppm
}

VARIATIONS = {
    "moisture": 15,      # ±15%
    "temperature": 5,    # ±5°C
    "humidity": 12,      # ±12%
    "rain": 3,           # ±3mm per day
    "light": 80,         # ±80 PPFD
    "co2": 100,          # ±100 ppm
}

UNITS = {
    "moisture": "%",
    "temperature": "°C",
    "humidity": "%",
    "rain": "mm/week",
    "light": "PPFD µmol/m²/s",
    "co2": "ppm"
}


def generate_realistic_measurements(playfield_serial, days=5):
    """Generate realistic sensor measurements for N days"""
    
    measurements_data = {}
    now = datetime.utcnow()
    
    for sensor_type in SENSOR_TYPES:
        measurements_data[sensor_type] = []
        
        if sensor_type == "rain":
            # Daily measurements for rain
            for day in range(days):
                measurement_time = now - timedelta(days=days-1-day, hours=12)
                base = BASE_VALUES["rain"]
                rain_value = base + random.uniform(-VARIATIONS["rain"], VARIATIONS["rain"])
                rain_value = max(0, rain_value)
                
                measurements_data[sensor_type].append({
                    "time": measurement_time,
                    "value": round(rain_value, 2)
                })
        else:
            # Hourly measurements for other sensors
            for day in range(days):
                for hour in range(24):
                    measurement_time = now - timedelta(
                        days=days-1-day,
                        hours=24-hour
                    )
                    
                    # Daily cycle: peak at midday (hour 12)
                    hour_factor = math.sin((hour - 6) * math.pi / 12)
                    
                    if sensor_type in ["temperature", "light"]:
                        # Peak during day
                        value = BASE_VALUES[sensor_type] + (hour_factor * VARIATIONS[sensor_type] * 0.7)
                    elif sensor_type == "humidity":
                        # Inverse of temperature
                        value = BASE_VALUES[sensor_type] - (hour_factor * VARIATIONS[sensor_type] * 0.6)
                    elif sensor_type == "moisture":
                        # Decreases during day, recovery at night
                        value = BASE_VALUES[sensor_type] - (hour_factor * VARIATIONS[sensor_type] * 0.5)
                    else:  # co2
                        # Slight daily cycle
                        value = BASE_VALUES[sensor_type] - (hour_factor * VARIATIONS[sensor_type] * 0.4)
                    
                    # Add random noise
                    value += random.uniform(-VARIATIONS[sensor_type] * 0.2, VARIATIONS[sensor_type] * 0.2)
                    value = max(0, value)  # Can't be negative
                    
                    measurements_data[sensor_type].append({
                        "time": measurement_time,
                        "value": round(value, 2)
                    })
    
    return measurements_data


def insert_measurements(playfield_serial, measurements_data):
    """Insert generated measurements into database"""
    
    robot = RobotZone.query.filter_by(serial_number=playfield_serial).first()
    if not robot:
        print(f"❌ Playfield {playfield_serial} not found")
        return False
    
    for sensor_type in SENSOR_TYPES:
        # Get or create sensor
        sensor = Sensor.query.filter_by(
            serial_number=playfield_serial,
            sensor_type=sensor_type
        ).first()
        
        if not sensor:
            sensor = Sensor(
                srnr_sensor=f"{playfield_serial}_{sensor_type}",
                sensor_type=sensor_type,
                unit=UNITS.get(sensor_type, ""),
                serial_number=playfield_serial
            )
            db.session.add(sensor)
            db.session.flush()
        else:
            # Delete old measurements to avoid duplicates
            Measurement.query.filter_by(srnr_sensor=sensor.srnr_sensor).delete()
        
        # Insert new measurements
        for data in measurements_data[sensor_type]:
            measurement = Measurement(
                value=data["value"],
                time_m=data["time"],
                srnr_sensor=sensor.srnr_sensor
            )
            db.session.add(measurement)
        
        print(f"  ✓ {sensor_type.capitalize()}: {len(measurements_data[sensor_type])} measurements")
    
    db.session.commit()
    return True


def main():
    parser = ArgumentParser(description="Generate sample sensor data")
    parser.add_argument("--playfield", "-p", required=True, help="Playfield serial number (e.g., RZ-001)")
    parser.add_argument("--days", "-d", type=int, default=5, help="Number of days to generate (default: 5)")
    
    args = parser.parse_args()
    
    with app.app_context():
        print("=" * 60)
        print("🌾 Sample Data Generator")
        print("=" * 60)
        
        print(f"\n📍 Playfield: {args.playfield}")
        print(f"📅 Days: {args.days}")
        
        # Generate data
        print("\n🔄 Generating measurements...")
        measurements_data = generate_realistic_measurements(args.playfield, args.days)
        
        # Insert into database
        print("\n📝 Inserting into database...")
        if insert_measurements(args.playfield, measurements_data):
            print(f"\n✅ Successfully generated {args.days} days of sample data")
            print("\nYou can now test plant recommendations with:")
            print(f"  python3 -m app.scripts.test_plant_recommendation")
        else:
            print("\n❌ Failed to insert measurements")
            sys.exit(1)


if __name__ == "__main__":
    main()
