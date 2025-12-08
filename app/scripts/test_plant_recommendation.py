#!/usr/bin/env python3
"""
Test script to verify plant recommendations work correctly

Usage:
    python3 -m app.scripts.test_plant_recommendation
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app import create_app, db
from app.routes.dashboard_routes import _get_average_measurements, _calculate_plant_health_score
from app.models import PlantProfile, RobotZone

app = create_app()

def main():
    with app.app_context():
        print("=" * 70)
        print("🤖 Plant Recommendation Test")
        print("=" * 70)

        playfield_serial = "RZ-001-A"
        
        # Get playfield
        robot = RobotZone.query.filter_by(serial_number=playfield_serial).first()
        if not robot:
            print(f"❌ Playfield {playfield_serial} not found")
            return False
        
        # Get average measurements
        print(f"\n📊 Getting average measurements for {playfield_serial} (last 5 days)...\n")
        avg_measurements = _get_average_measurements(playfield_serial, days=5)
        
        if not avg_measurements:
            print("❌ No measurements found")
            return False
        
        for sensor_type, value in avg_measurements.items():
            if value is not None:
                print(f"  {sensor_type:15s} {value:8.2f}")
        
        # Get all plants and calculate scores
        print("\n🌱 Plant Compatibility Scores:\n")
        
        all_plants = PlantProfile.query.all()
        plant_rankings = []
        
        for plant in all_plants:
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
            score = _calculate_plant_health_score(avg_measurements, plant_data)
            if score is not None:
                plant_rankings.append({
                    'key': plant.key,
                    'name': plant.display_name,
                    'score': round(score, 2)
                })
        
        plant_rankings.sort(key=lambda x: x['score'], reverse=True)
        
        for i, rec in enumerate(plant_rankings, 1):
            bar_length = int(rec['score'] / 5)
            bar = '█' * bar_length + '░' * (20 - bar_length)
            print(f"  {rec['name']:20s} {bar} {rec['score']:6.2f}%")
        
        if plant_rankings:
            top_plant = plant_rankings[0]
            print(f"\n✨ RECOMMENDATION: {top_plant['name']} ({top_plant['score']}%)")
            return True
        else:
            print("\n❌ No plants could be scored")
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
