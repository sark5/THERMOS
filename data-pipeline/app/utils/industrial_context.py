def calculate_industrial_context(
        distance_meters,
        facility_type,
        criticality=None
):
    """Calculate an explainable industrial-context score.

       This is a feature, not a classification label.
    """
    if distance_meters is None:
        return 0.0

    distance = float(distance_meters)
    if distance <= 100:
        distance_score = 1.0
    elif distance <= 250:
        distance_score = 0.85
    elif distance <= 500:
        distance_score = 0.50
    elif distance <= 1000:
        distance_score = 0.45
    elif distance <= 3000:
        distance_score = 0.20
    else:
        distance_score = 0.0

    type_score = 0.20
    criticality_score = 0.20
    if facility_type:
        value = str(facility_type).lower()
        high_priority = [
            "refinery",
            "chemical",
            "petrochemical",
            "power",
            "plant",
            "oil",
            "gas",
            "works",
        ]
        medium_priority = [
            "industrial",
            "factory",
            "mine",
            "quarry",
        ]
        if any(key in value for key in high_priority):
            type_score = 1.0
        elif any(key in value for key in medium_priority):
            type_score = 0.65

    if criticality:
        value = str(criticality).lower()
        criticality_score = {
            "critical": 1.0,
            "high": 0.80,
            "medium": 0.55,
            "low": 0.25,
        }.get(value, 0.20)

    score = (
        distance_score * 0.50
        + type_score * 0.30
        + criticality_score * 0.20
    )

    return round(
        min(max(score, 0.0), 1.0),
        4
    )
