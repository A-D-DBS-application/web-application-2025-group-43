#!/usr/bin/env python3
"""
Script to add a demo user with garden, playfield, and sensor data
for testing and presentation purposes.
"""

from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Garden, RobotZone, Sensor, Measurement, PlantProfile
from werkzeug.security import generate_password_hash

app = create_app()

def _get_unit(sensor_type):
    """Get unit for sensor type"""
    units = {
        "moisture": "%",
        "temperature": "°C",
        "humidity": "%",
        "rain": "mm",
        "light": "µmol/m²/s",
        "co2": "ppm"
    }
    return units.get(sensor_type, "")

def add_demo_user():
    """Add demo user fretje@capenta.com with garden, playfield, and good sensor data"""
    
    with app.app_context():
        # Check if user already exists
        existing_user = User.query.filter_by(uemail="fretje@capenta.com").first()
        if existing_user:
            print("✅ Demo user already exists!")
            return existing_user
        
        # 1. Create user
        print("📝 Creating demo user...")
        demo_user = User(
            uemail="fretje@capenta.com",
            uname="Fretje Demo",
            phone="+31612345678",
            adress="Demo Street 123, Amsterdam",
            password=generate_password_hash("demo123")
        )
        db.session.add(demo_user)
        db.session.flush()
        print(f"  ✓ User created: {demo_user.uemail}")
        
        # 2. Create garden
        print("🌳 Creating garden...")
        garden = Garden(
            garden_id=uuid.uuid4(),
            garden_name="Demo Garden",
            adress_garden="Demo Street 123, Amsterdam",
            area_garden=Decimal("50"),
            user_email="fretje@capenta.com"
        )
        db.session.add(garden)
        db.session.flush()
        print(f"  ✓ Garden created: {garden.garden_name} ({garden.garden_id})")
        
        # 3. Get a good plant (Basil is usually good for indoor farming)
        print("🌱 Finding good plant profile...")
        plant = PlantProfile.query.filter_by(key="basil").first()
        if not plant:
            plant = PlantProfile.query.first()
        print(f"  ✓ Selected plant: {plant.display_name}")
        print(f"    Moisture: {plant.soil_moisture_mean}% ± {plant.soil_moisture_std}")
        print(f"    Temp: {plant.temperature_mean}°C ± {plant.temperature_std}")
        print(f"    Humidity: {plant.humidity_mean}% ± {plant.humidity_std}")
        
        # 4. Create playfield/robot_zone
        print("🤖 Creating playfield...")
        serial_number = "DEMO-001"
        robot_zone = RobotZone(
            serial_number=serial_number,
            robot_name="Demo Playfield",
            area_playfield=Decimal("1"),
            garden_id=garden.garden_id,
            plant_profile_id=plant.id
        )
        db.session.add(robot_zone)
        db.session.flush()
        print(f"  ✓ Playfield created: {robot_zone.robot_name} ({serial_number})")
        
        # 5. Create sensors for all sensor types
        print("📊 Creating sensors...")
        sensor_types = ["moisture", "temperature", "humidity", "rain", "light", "co2"]
        sensors = {}
        
        for sensor_type in sensor_types:
            srnr = f"SENSOR-{serial_number}-{sensor_type.upper()}"
            sensor = Sensor(
                srnr_sensor=srnr,
                sensor_type=sensor_type,
                unit=_get_unit(sensor_type),
                serial_number=serial_number
            )
            db.session.add(sensor)
            db.session.flush()
            sensors[sensor_type] = sensor
            print(f"  ✓ Sensor created: {sensor_type} ({srnr})")
        
        # 6. Create measurement data for the last 5 days
        # Data should be optimal for the plant to get 80+ score
        print("📈 Adding measurement data (5 days of optimal data)...")
        
        measurements_config = {
            "moisture": plant.soil_moisture_mean,      # Use optimal mean
            "temperature": plant.temperature_mean,
            "humidity": plant.humidity_mean,
            "rain": plant.rain_mm_week_mean / 7,       # Daily average
            "light": plant.ppfd_mean,
            "co2": plant.co2_mean,
        }
        
        now = datetime.utcnow()
        total_measurements = 0
        
        # Create measurements for last 5 days, ~4-5 per day
        for day_offset in range(5):
            date = now - timedelta(days=day_offset)
            
            for hour_offset in range(5):  # 5 measurements per day
                time = date - timedelta(hours=hour_offset * 4)  # Every ~4 hours
                
                for sensor_type, optimal_value in measurements_config.items():
                    sensor = sensors[sensor_type]
                    
                    # Add slight random variation (±5% of optimal)
                    variance = optimal_value * 0.05
                    import random
                    value = optimal_value + random.uniform(-variance, variance)
                    
                    measurement = Measurement(
                        value=Decimal(str(round(value, 2))),
                        time_m=time,
                        srnr_sensor=sensor.srnr_sensor
                    )
                    db.session.add(measurement)
                    total_measurements += 1
        
        db.session.commit()
        print(f"  ✓ Added {total_measurements} measurement records")
        
        # 7. Calculate and display expected score
        print("\n" + "="*60)
        print("✅ DEMO USER SUCCESSFULLY CREATED!")
        print("="*60)
        print(f"\nLogin credentials:")
        print(f"  Email: fretje@capenta.com")
        print(f"  Password: demo123")
        print(f"\nCreated resources:")
        print(f"  Garden: {garden.garden_name}")
        print(f"  Playfield: {robot_zone.robot_name} ({serial_number})")
        print(f"  Plant: {plant.display_name}")
        print(f"  Sensors: {len(sensors)} active")
        print(f"  Data points: {total_measurements} measurements")
        print(f"\nExpected health score: 80+ (data optimized for {plant.display_name})")
        print("="*60 + "\n")
        
        return demo_user

if __name__ == "__main__":
    add_demo_user()
