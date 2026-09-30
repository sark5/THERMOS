ALTER TABLE thermos.thermal_events
ADD COLUMN IF NOT EXISTS firms_type INTEGER;

CREATE INDEX IF NOT EXISTS
idx_thermal_firms_type
ON thermos.thermal_events(firms_type);