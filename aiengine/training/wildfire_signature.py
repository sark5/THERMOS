def wildfire_signature(
    forest_context,
    spatial_spread,
    temporal_growth,
    industrial_context
):

    score = (
        forest_context * 0.40
        + spatial_spread * 0.30
        + temporal_growth * 0.20
        + (1 - industrial_context) * 0.10
    )

    return round(
        min(
            max(score, 0),
            1
        ),
        4
    )