#!/usr/bin/env python3
"""Add score_date column to health_score table"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        print("🔄 Adding score_date column to health_score table...")
        
        # Check if column already exists
        result = db.session.execute(text("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'health_score' AND column_name = 'score_date'
            )
        """)).scalar()
        
        if result:
            print("✅ score_date kolom bestaat al")
        else:
            print("📝 Voeg score_date kolom toe...")
            db.session.execute(text("ALTER TABLE health_score ADD COLUMN score_date DATE"))
            
            print("📝 Vul score_date in met bestaande calculated_at data...")
            db.session.execute(text("""
                UPDATE health_score SET score_date = CAST(calculated_at AS DATE) 
                WHERE score_date IS NULL
            """))
            
            db.session.commit()
            print("✅ Migration completed!")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.session.rollback()
        sys.exit(1)
