def wildfire_evidence(
    row
):

    firms_type = row.get(
        "firms_type"
    )

    forest_context = float(
        row.get(
            "forest_context",
            0.0
        ) or 0.0
    )

    agricultural_context = float(
        row.get(
            "agricultural_context",
            0.0
        ) or 0.0
    )

    industrial_context = float(
        row.get(
            "industrial_context",
            0.0
        ) or 0.0
    )

    persistence = float(
        row.get(
            "persistence_score",
            0.0
        ) or 0.0
    )

    anomaly = float(
        row.get(
            "anomaly_score",
            0.0
        ) or 0.0
    )

    score = 0.0
    reasons = []

    if firms_type == 0:

        score += 0.30

        reasons.append(
            "FIRMS identifies a presumed vegetation fire"
        )

    score += (
        forest_context * 0.45
    )

    if forest_context >= 0.70:

        reasons.append(
            "Strong forest/vegetation context"
        )

    score += (
        (1.0 - industrial_context)
        * 0.10
    )

    score += (
        (1.0 - agricultural_context)
        * 0.05
    )

    score += (
        persistence * 0.05
    )

    score += (
        anomaly * 0.05
    )

    return {
        "score": round(
            min(score, 1.0),
            4
        ),
        "reasons": reasons,
    }