-- SQL Migration Script: Voeg health_score tabel toe
-- Dit script voegt de health_score tabel toe aan de database
-- Run dit in Supabase SQL Editor of via psql command line

CREATE TABLE IF NOT EXISTS health_score (
    hid BIGSERIAL PRIMARY KEY,
    score DOUBLE PRECISION NOT NULL,
    score_date DATE NOT NULL,
    calculated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    serial_number VARCHAR NOT NULL,
    FOREIGN KEY (serial_number) REFERENCES robot_zone(serial_number) ON DELETE CASCADE,
    UNIQUE(serial_number, score_date)
);

-- Index voor snelle queries op serial_number en score_date
CREATE INDEX IF NOT EXISTS idx_health_score_serial_date 
    ON health_score(serial_number, score_date DESC);

-- Index voor trend-queries
CREATE INDEX IF NOT EXISTS idx_health_score_serial_limit
    ON health_score(serial_number, calculated_at DESC);
