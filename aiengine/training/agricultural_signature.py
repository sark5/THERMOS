def agricultural_signature(
    cropland_context,
    seasonality,
    short_duration,
    industrial_context,
    spatial_clustering
):

    score = (
        cropland_context * 0.35
        + seasonality * 0.20
        + short_duration * 0.15
        + (1 - industrial_context) * 0.15
        + spatial_clustering * 0.15
    )

    return round(
        min(
            max(score, 0),
            1
        ),
        4
    )