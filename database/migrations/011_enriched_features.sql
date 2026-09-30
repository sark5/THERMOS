ALTER TABLE thermos.thermal_events
ADD COLUMN IF NOT EXISTS
    distance_to_facility DOUBLE PRECISION;

ALTER TABLE thermos.thermal_events
ADD COLUMN IF NOT EXISTS
    industrial_context DOUBLE PRECISION;

ALTER TABLE thermos.thermal_events
ADD COLUMN IF NOT EXISTS
    historical_observation_count INTEGER;

ALTER TABLE thermos.thermal_events
ADD COLUMN IF NOT EXISTS
    historical_active_days INTEGER;

ALTER TABLE thermos.thermal_events
ADD COLUMN IF NOT EXISTS
    historical_mean_frp DOUBLE PRECISION;

ALTER TABLE thermos.thermal_events
ADD COLUMN IF NOT EXISTS
    historical_stddev_frp DOUBLE PRECISION;