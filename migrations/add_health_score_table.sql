-- SQL Migration Script: Voeg health_score tabel toe
-- Dit script voegt de health_score tabel toe aan de database
-- Run dit in Supabase SQL Editor of via psql command line

CREATE TABLE IF NOT EXISTS health_score (
    hid BIGSERIAL PRIMARY KEY,
    score DOUBLE PRECISION NOT NULL,
    score_date DATE,
    calculated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    serial_number VARCHAR NOT NULL,
    FOREIGN KEY (serial_number) REFERENCES robot_zone(serial_number) ON DELETE CASCADE
);

-- Voeg score_date kolom toe aan bestaande tabel (idempotent)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'health_score' AND column_name = 'score_date'
  ) THEN
    ALTER TABLE health_score ADD COLUMN score_date DATE;
    
    -- Vul score_date in op basis van calculated_at voor bestaande records
    UPDATE health_score SET score_date = CAST(calculated_at AS DATE) WHERE score_date IS NULL;
  END IF;
END $$;

-- Index voor snelle queries op serial_number en score_date
CREATE INDEX IF NOT EXISTS idx_health_score_serial_date 
    ON health_score(serial_number, score_date DESC);

-- Index voor trend-queries
CREATE INDEX IF NOT EXISTS idx_health_score_serial_calc
    ON health_score(serial_number, calculated_at DESC);
