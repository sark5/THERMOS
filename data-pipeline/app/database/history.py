from datetime import datetime
def save_thermal_history(
        connection,record
):
    query="""
INSERT INTO thermos.thermal_history(
    facility_id,
    latitude,longitude,
    observation_count,
    active_days,
    first_seen,
    last_seen,
    mean_frp,
    median_frp,
    max_frp,
    min_frp,
    frp_stddev,
    persistence_score,
    anomaly-score,
    thermal_status
    )
    VALUES(
        %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s
    )
    """
    with connection.cursor() as cursor:
        cursor.execute(
            query,
            (
                record.get("facility_id"),
                record["latitude"],
                record["longitude"],
                record["observation_count"],
                record["active_days"],
                record.get("first_seen"),
                record.get("last_seen"),
                record["mean_frp"],
                record["median_frp"],
                record["max_frp"],
                record["min_frp"],
                record["frp_stddev"],
                record["persistence_score"],
                record["anomaly_score"],
                record["thermal_status"],
            )
        )
    connection.commit()