def attribution_confidence(
    distance_meters,
    facility_type
):

    if distance_meters is None:
        return 0.0

    distance = float(
        distance_meters
    )

    if distance <= 100:
        distance_score = 1.0

    elif distance <= 250:
        distance_score = 0.85

    elif distance <= 500:
        distance_score = 0.65

    elif distance <= 1000:
        distance_score = 0.40

    else:
        distance_score = 0.10

    type_score = 0.20

    if facility_type:

        value = (
            str(
                facility_type
            ).lower()
        )

        if any(
            key in value
            for key in [
                "refinery",
                "chemical",
                "power",
                "petrochemical",
                "oil",
                "gas",
            ]
        ):
            type_score = 1.0

        elif any(
            key in value
            for key in [
                "industrial",
                "factory",
                "works",
                "mine",
            ]
        ):
            type_score = 0.65

    return round(
        distance_score * 0.7
        + type_score * 0.3,
        4
    )