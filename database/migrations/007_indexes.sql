CREATE INDEX IF NOT EXISTS idx_thermal_location
ON thermos.thermal_events
USING GIST(location);

CREATE INDEX IF NOT EXISTS idx_thermal_time
ON thermos.thremal_events(acquired_at DESC);

CREATE INDEX IF NOT EXISTS idx_thermal_classification
ON thermos.thermal_events(facility_id);

CREATE INDEX IF NOT EXISTS idx_thermal_facility
ON thermos.thermal_events(facility_id);

CREATE INDEX IF NOT EXISTS idx_thermal_frp
ON thermos.thermal_events(frp);