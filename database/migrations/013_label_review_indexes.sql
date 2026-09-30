CREATE INDEX IF NOT EXISTS
idx_label_reviews_event
ON thermos.label_reviews(event_id);

CREATE INDEX IF NOT EXISTS
idx_label_reviews_status
ON thermos.label_reviews(review_status);

CREATE INDEX IF NOT EXISTS
idx_label_reviews_label
ON thermos.label_reviews(human_label);

CREATE INDEX IF NOT EXISTS
idx_label_reviews_source
ON thermos.label_reviews(source_id);