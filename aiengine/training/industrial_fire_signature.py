def industrial_fire_signature(
    industrial_context,
    anomaly,
    frp_spike,
    persistence
):

    score = (
        industrial_context * 0.35
        + anomaly * 0.35
        + frp_spike * 0.25
        + (1 - persistence) * 0.05
    )

    return round(
        min(
            max(score, 0),
            1
        ),
        4
    )