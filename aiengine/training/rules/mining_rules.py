def mining_evidence(
    row
):

    facility_type = str(
        row.get(
            "facility_type",
            ""
        )
    ).lower()

    distance = row.get(
        "distance_to_facility"
    )

    industrial_context = float(
        row.get(
            "industrial_context",
            0.0
        ) or 0.0
    )

    score = 0.0
    reasons = []

    if (
        "mine" in facility_type
        or "quarry" in facility_type
    ):

        score += 0.60

        reasons.append(
            "Near mining/quarry infrastructure"
        )

    if distance is not None:

        try:
            distance = float(
                distance
            )

            if distance <= 1000:

                score += 0.25

                reasons.append(
                    "Thermal anomaly is within "
                    "1 km of mining infrastructure"
                )

        except (
            ValueError,
            TypeError
        ):
            pass

    score += (
        industrial_context * 0.15
    )

    return {
        "score": round(
            min(score, 1.0),
            4
        ),
        "reasons": reasons,
    }