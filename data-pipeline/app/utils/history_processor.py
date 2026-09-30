from collections import defaultdict
from aiengine.app.preprocessing.persistence import(
    calculate_persistence_score,
    calculate_frp_anomaly
)
from aiengine.app.models.thermal_status import (
    determine_thermal_status
)
def group_events_by_facility(events):
    grouped=defaultdict(list)
    for event in events:
        facility_id=event.get("facility_id")
        if facility_id is not None:
            grouped[facility_id].append(event)
    return grouped
def process_facility_history(events):
    if not events:
        return None
    frp_values=[
        float(event["frp"])
        for event in events
        if event.get("frp") is not None
    ]
    if not frp_values:
        return None
    observation_count=len(events)
    active_days=len(
        {
            event["acquired_at"].date()
            for event in events
            if event.get("acquired_at")
        }
    )
    mean_frp=sum(frp_values)/len(frp_values)
    max_frp=max(frp_values)
    min_frp=min(frp_values)
    if len(frp_values)>1:
        variance=sum((value-mean_frp)** 2 
        for value in frp_values
        ) /len(frp_values)
        stddev=variance**0.5
    else:
        stddev=0.0
        current_frp=frp_values[-1]
        persistence_score=calculate_persistence_score(observation_count,active_days)
        anomaly_score=calculate_frp_anomaly(current_frp,mean_frp,stddev)
        status=determine_thermal_status(persistence_score,anomaly_score)
        latest=events[-1]
        return{
            "facility_id":latest.get("facility_id"),
            "latitude":latest["latitude"],
            "longitude":latest["longitude"],
            "observation_count":observation_count,
            "active_days":active_days,
            "first_seen":events[0].get("acquired_at"),
            "last_seen":events[-1].get("acquired_at"),
            "mean_frp":mean_frp,
            "median_frp":sorted(frp_values),
            "max_frp":max_frp,
            "min_frp":min_frp,
            "frp_stddev":stddev,
            "persistence_score":persistence_score,
            "anomaly_score":anomaly_score,
            "thermal_status":status
        }
