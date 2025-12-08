#!/usr/bin/env python3
"""
Setup test environment with demo user, garden, and playfield

Usage:
    python3 -m app.scripts.setup_test_environment
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app import create_app, db
from app.models import User, Garden, RobotZone, Sensor
from datetime import datetime

app = create_app()

def main():
    with app.app_context():
        # Check if demo user exists
        user = User.query.filter_by(uname="demo").first()
        if not user:
            user = User(uemail="demo@capenta.dev", uname="demo", password="demo1234")
            db.session.add(user)
            db.session.commit()
            print("✅ Created demo user (demo / demo1234)")
        else:
            print("⊙ Demo user already exists")

        # Check if demo garden exists
        garden = Garden.query.filter_by(garden_name="Demo Garden").first()
        if not garden:
            garden = Garden(
                garden_name="Demo Garden",
                adress_garden="Amsterdam",
                user_email=user.uemail
            )
            db.session.add(garden)
            db.session.commit()
            print("✅ Created demo garden")
        else:
            print("⊙ Demo garden already exists")

        # Check if demo playfield exists
        playfield = RobotZone.query.filter_by(serial_number="RZ-001-A").first()
        if not playfield:
            # First ensure all sensors exist for this serial
            for sensor_type in ["moisture", "temperature", "humidity", "rain", "light", "co2"]:
                sensor = Sensor.query.filter_by(serial_number="RZ-001-A", sensor_type=sensor_type).first()
                if not sensor:
                    sensor = Sensor(
                        srnr_sensor=f"S-{sensor_type.upper()}-001",
                        sensor_type=sensor_type, 
                        unit="%" if sensor_type in ["moisture", "humidity"] else
                             "°C" if sensor_type == "temperature" else
                             "mm/week" if sensor_type == "rain" else
                             "uur/dag" if sensor_type == "light" else "ppm",
                        serial_number="RZ-001-A"
                    )
                    db.session.add(sensor)
            db.session.commit()
            
            playfield = RobotZone(
                serial_number="RZ-001-A",
                garden_id=garden.garden_id
            )
            db.session.add(playfield)
            db.session.commit()
            print("✅ Created demo playfield RZ-001-A")
        else:
            print("⊙ Demo playfield already exists")

        print("\n✨ Test environment ready!")
        print("   Login: demo / demo1234")
        print("   Garden: Demo Garden")
        print("   Playfield: Demo Playfield (RZ-001-A)")

if __name__ == "__main__":
    main()
