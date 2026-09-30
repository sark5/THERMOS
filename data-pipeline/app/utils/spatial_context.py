def caluacte_industrial_context(
    distance_meters,
    facility_type
):
    score=0.0
    if distance_meters <=250:
        score+=0.60
    elif distance_meters<=500:
        score+=0.45
    elif distance_meters<=1000:
        score+=0.25
    elif distance_meters<=3000:
        score+=0.10
    high_priority_types={
        "refinery",
        "power",
        "works",
        "chemical",
        "industial",
        "plant",
        "mine"
    }
    if facility_type:
        facility_type_lower={
           facility_type.lower()
        }
        for value in high_priority_types:
            if value in facility_type_lower:
                score+=0.20
                break

    return min(
        score,
        1.0
    )
      