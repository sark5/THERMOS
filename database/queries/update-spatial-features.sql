UPDATE thermos.thermal_events e
SET
    facility_id = nearest.id,
    distance_to_facility =
        ST_Distance(
            e.location::geography,
            nearest.location::geography
        )
FROM LATERAL (
    SELECT
        f.id,
        f.location
    FROM thermos.facilities f
    ORDER BY
        e.location <-> f.location
    LIMIT 1
) nearest;