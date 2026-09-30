from datetime import datetime
def calculate_temporal_features(events):
    if not events:
        return {
            "observation_count":0,
            "active_days":0,
            "duration_hours":0,
            "mean_frp":0.0,
            "max_frp":0.0
        }
    timestamps=[]
    frp_values=[]
    active_dates=set()
    for event in events:
        acquired_at=event.get("acquired_at")
        if acquired_at:
            if isinstance(acquired_at,str):
                acquired_at=datetime.fromisoformat(
                    acquired_at.replace("Z","+00.00")
                )
            timestamps.append(acquired_at)
            active_dates.add(acquired_at.date())
        frp=event.get("frp")
        if frp is not None:
            frp_values.append(float(frp))
    duration_hours=0
    if len(timestamps)>=2:
        duration=(
            max(timestamps)-min(timestamps)
        )
        duration_hours=round(
            duration.total_seconds()/3600,2
        )
    return {
        "observation_count":len(events),
        "active_days":len(active_dates),
        "duration_hours":duration_hours,
        "mean_frp":(
            sum(frp_values)/len(frp_values)
            if frp_values else 0.0
        ),
        "max_frp":(
            max(frp_values)
            if frp_values else 0.0
        )
    }
