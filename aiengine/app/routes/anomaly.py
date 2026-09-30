from fastapi import APIRouter
from pydantic import BaseModel

from app.inference.persistence_engine import (
    analyze_thermal_history
)


router = APIRouter()


class ThermalHistoryRequest(BaseModel):

    observation_count: int
    active_days: int

    current_frp: float
    historical_mean_frp: float
    historical_stddev: float

    observation_window_days: int = 30


@router.post("/thermal-history")
def analyze_history(
    request: ThermalHistoryRequest
):

    result = analyze_thermal_history(
        observation_count=request.observation_count,
        active_days=request.active_days,
        current_frp=request.current_frp,
        historical_mean_frp=request.historical_mean_frp,
        historical_stddev=request.historical_stddev,
        observation_window_days=request.observation_window_days
    )

    return result

