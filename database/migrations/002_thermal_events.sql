CREATE TABLE IF NOT EXISTS thermos.thermal_events (

    id BIGSERIAL PRIMARY KEY,

    event_id VARCHAR(120) UNIQUE NOT NULL,

    source VARCHAR(50) NOT NULL,

    satellite VARCHAR(50),

    latitude DOUBLE PRECISION NOT NULL,

    longitude DOUBLE PRECISION NOT NULL,

    location GEOMETRY(Point, 4326) NOT NULL,

    acquired_at TIMESTAMPTZ NOT NULL,

    brightness DOUBLE PRECISION,

    bright_t31 DOUBLE PRECISION,

    frp DOUBLE PRECISION,

    confidence DOUBLE PRECISION,

    day_night VARCHAR(1),

    scan DOUBLE PRECISION,

    track DOUBLE PRECISION,

    classification VARCHAR(100),

    classification_confidence DOUBLE PRECISION,

    persistence_score DOUBLE PRECISION,

    anomaly_score DOUBLE PRECISION,

    risk_score DOUBLE PRECISION,

    risk_level VARCHAR(30),

    facility_id BIGINT,

    satellite_image_url TEXT,

    ai_explanation JSONB,

    metadata JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    updated_at TIMESTAMPTZ DEFAULT NOW()
);