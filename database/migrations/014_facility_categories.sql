-- Migration 014: Additional spatial indexes and facility categories

CREATE INDEX IF NOT EXISTS idx_facilities_location ON thermos.facilities USING GIST (location);
CREATE INDEX IF NOT EXISTS idx_facilities_type ON thermos.facilities (facility_type);

ALTER TABLE thermos.thermal_events
ADD COLUMN IF NOT EXISTS distance_to_powerplant DOUBLE PRECISION,
ADD COLUMN IF NOT EXISTS distance_to_refinery DOUBLE PRECISION,
ADD COLUMN IF NOT EXISTS distance_to_mine DOUBLE PRECISION,
ADD COLUMN IF NOT EXISTS distance_to_quarry DOUBLE PRECISION,
ADD COLUMN IF NOT EXISTS distance_to_flare DOUBLE PRECISION,
ADD COLUMN IF NOT EXISTS inside_facility_boundary BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS nearest_facility_count_500m INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS nearest_facility_count_1km INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS industrial_facility_density DOUBLE PRECISION DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS mining_context DOUBLE PRECISION DEFAULT 0.0;
