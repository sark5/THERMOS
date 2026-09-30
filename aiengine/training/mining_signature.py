def mining_signature(
    mining_context,
    spatial_clustering,
    bare_land_context,
    persistence
):

    score = (
        mining_context * 0.40
        + spatial_clustering * 0.25
        + bare_land_context * 0.20
        + persistence * 0.15
    )

    return round(
        min(
            max(score, 0),
            1
        ),
        4
    )