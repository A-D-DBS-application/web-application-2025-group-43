#!/usr/bin/env python3
"""
Script om de health_score tabel te maken in de Supabase database.
Run dit als: python3 -m app.scripts.create_health_score_table
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app import create_app, db
from app.models import HealthScore

def main():
    app = create_app()
    
    with app.app_context():
        print("Creating health_score table...")
        
        # SQLAlchemy genereert en voert de CREATE TABLE uit
        db.create_all()
        
        # Controleer of de tabel is aangemaakt
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'health_score' in tables:
            print("✅ health_score tabel succesvol aangemaakt!")
            columns = inspector.get_columns('health_score')
            print("\nTabelstructuur:")
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
        else:
            print("❌ Fout: health_score tabel niet aangemaakt")

if __name__ == "__main__":
    main()
