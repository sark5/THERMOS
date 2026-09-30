from app.preprocessing.persistence import (
    calculate_frp_anomaly,
    calculate_persistence_score
)

from app.models.thermal_status import (
    determine_thermal_status
)


def analyze_thermal_history(
    observation_count: int,
    active_days: int,
    current_frp: float,
    historical_mean_frp: float,
    historical_stddev: float,
    observation_window_days: int = 30
):

    persistence_score = calculate_persistence_score(
        observation_count=observation_count,
        active_days=active_days,
        observation_window_days=observation_window_days
    )

    anomaly_score = calculate_frp_anomaly(
        current_frp=current_frp,
        historical_mean=historical_mean_frp,
        historical_stddev=historical_stddev
    )

    thermal_status = determine_thermal_status(
        persistence_score=persistence_score,
        anomaly_score=anomaly_score
    )

    return {
        "persistence_score": persistence_score,
        "anomaly_score": anomaly_score,
        "thermal_status": thermal_status
    }

