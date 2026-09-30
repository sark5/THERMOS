def agricultural_evidence(
    row
):

    firms_type = row.get(
        "firms_type"
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

    forest_context = float(
        row.get(
            "forest_context",
            0.0
        ) or 0.0
    )

    score = 0.0
    reasons = []

    if firms_type == 0:
        score += 0.35

        reasons.append(
            "FIRMS identifies a presumed vegetation fire"
        )

    score += (
        agricultural_context * 0.45
    )

    if agricultural_context >= 0.70:

        reasons.append(
            "Strong agricultural land context"
        )

    score += (
        (1.0 - industrial_context)
        * 0.15
    )

    score += (
        (1.0 - forest_context)
        * 0.05
    )

    return {
        "score": round(
            min(score, 1.0),
            4
        ),
        "reasons": reasons,
    }