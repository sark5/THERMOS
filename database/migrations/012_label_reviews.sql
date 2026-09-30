CREATE TABLE IF NOT EXISTS thermos.label_reviews (
    id BIGSERIAL PRIMARY KEY,

    event_id BIGINT NOT NULL,

    source_id VARCHAR(120),

    weak_label VARCHAR(50),

    weak_label_score DOUBLE PRECISION,

    human_label VARCHAR(50),

    review_status VARCHAR(30) NOT NULL DEFAULT 'PENDING',

    reviewer VARCHAR(255),

    review_notes TEXT,

    reviewed_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT fk_review_event
        FOREIGN KEY (event_id)
        REFERENCES thermos.thermal_events(id),

    CONSTRAINT valid_review_status
        CHECK (
            review_status IN (
                'PENDING',
                'VALIDATED',
                'CORRECTED',
                'UNCERTAIN',
                'REJECTED'
            )
        )
);