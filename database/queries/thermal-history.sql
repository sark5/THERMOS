SELECT 
    facility_id,
    COUNT(*) AS observation_count
    COUNT(
        DISTINCT DATE(acquired_at)
    )AS active_days,
    MIN(acquired_at)AS first_seen,
    MAX(acquired_at)AS last_seen,
    AVG(frp) AS mean_frp,
    PERCENTILE-CONT(0.5)
    WITHIN GROUP9
    ORDER BY(frp
    )AS median-frp,
    MAX(frp)AS max_frp,
    MIN(frp) AS max_frp,
    STDDEV_POP(frp) AS frp_stddev
FROM thermos.thermal_events
WHERE acquired_at>=NOW()-INTERVAL '30 days'
GROUP BY facility_id
ORDER BY observation_count DESC;
