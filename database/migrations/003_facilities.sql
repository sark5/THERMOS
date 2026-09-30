CREATE TABLE IF NOT EXISTS thermos.facilities(
    id BIGSERIAL PRIMARY KEY,
    osm_id VARCHAR(100) UNIQUE,
    name VARCHAR(255),
    facility_type VARCHAR(100),
    operator VARCHAR(255),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    location GEOMETRY(Point, 4326),
    boundary GEOMETRY(MultiPolygon, 4326),
    criticality VARCHAR(100),
    country VARCHAR(100),
    state VARCHAR(100),
    district VARCHAR(100),
    source VARCHAR(100),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);