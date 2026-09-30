from statistics import mean,median,stdev

def calculate_persistence_score(
        observation_count:int,
        active_days:int,
        observation_window_days:int
)->float:
    if observation_count<=0:
        return 0.0
    frequency_score=min(observation_count/20.0,1.0)
    day_score=min(active_days/float(observation_window_days),1.0)
    persistence_score=(frequency_score* 0.5
                       +day_score*0.5)
    return round(min(persistence_score,1.0),4)
def calculate_frp_statistics(frp_values):
    if not frp_values:
        return {
            "mean":0.0,
            "median":0.0,
            "max":0.0,
            "min":0.0,
            "stddev":0.0
        }
    values=[
        float(value)
        for value in frp_values
        if value is not None
    ]
    if not values:
        return{
            "mean":0.0,
            "median":0.0,
            "max":0.0,
            "min":0.0,
            "stddev":0.0
        }
    return {
        "mean":round(mean(values),4),
        "median":round(median(values),4),
        "max":round(max(values),4),
        "min":round(min(values),4),
        "stddev":round(
            stdev(values) if len(values) >1 else 0.0,
            4
        )
    }
def calculate_frp_anomaly(
        current_frp:float,
        historical_mean:float,
        historical_stddev:float
)->float:
    if historical_stddev<=0:
        if current_frp>historical_mean:
            return 1.0
        return 0.0
    z_score=(
        current_frp-historical_mean
    )/historical_stddev
    if z_score<=0:
        return 0.0
    anomaly=min(z_score/5.0,1.0)
    return round(anomaly,4)
