WITH event_history AS (

    SELECT
        e.id AS event_pk,

        COUNT(h.id) AS observation_count_30d,

        COUNT(
            DISTINCT DATE(h.acquired_at)
        ) AS active_days_30d,

        AVG(h.frp) AS mean_frp_30d,

        STDDEV_POP(h.frp)
            AS stddev_frp_30d,

        MAX(h.frp) AS max_frp_30d

    FROM thermos.thermal_events e

    LEFT JOIN thermos.thermal_events h
        ON h.acquired_at
            BETWEEN
                e.acquired_at - INTERVAL '30 days'
                AND e.acquired_at

        AND ST_DWithin(
            e.location::geography,
            h.location::geography,
            1000
        )

    GROUP BY e.id
)

SELECT
    e.id AS event_pk,
    e.event_id,

    e.latitude,
    e.longitude,

    e.brightness,
    e.bright_t31,
    e.frp,

    e.confidence,
    e.day_night,
    e.scan,
    e.track,

    e.satellite,
    e.acquired_at,

    f.id AS facility_id,
    f.name AS facility_name,
    f.facility_type,
    NULL AS criticality,

    ROUND(
        ST_Distance(
            e.location::geography,
            f.location::geography
        )::numeric,
        2
    ) AS distance_to_facility,

    eh.observation_count_30d,
    eh.active_days_30d,
    eh.mean_frp_30d,
    eh.stddev_frp_30d,
    eh.max_frp_30d

FROM thermos.thermal_events e

LEFT JOIN LATERAL (

    SELECT
        f.*

    FROM thermos.facilities f

    ORDER BY
        e.location <-> f.location

    LIMIT 1

) f ON TRUE

LEFT JOIN event_history eh
    ON eh.event_pk = e.id

ORDER BY e.acquired_at;