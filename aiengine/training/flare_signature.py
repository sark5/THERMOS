import numpy as np


def flare_signature(
    persistence,
    stability,
    industrial_context,
    anomaly,
    periodicity
):

    score = (
        persistence * 0.30
        + stability * 0.25
        + industrial_context * 0.25
        + periodicity * 0.15
        + (1 - anomaly) * 0.05
    )

    return round(
        min(
            max(score, 0),
            1
        ),
        4
    )