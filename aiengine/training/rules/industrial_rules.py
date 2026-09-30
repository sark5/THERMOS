from typing import Dict, List


def industrial_context_score(
    row
) -> float:

    value = float(
        row.get(
            "industrial_context",
            0.0
        ) or 0.0
    )

    return min(
        max(value, 0.0),
        1.0
    )


def facility_distance_score(
    row
) -> float:

    distance = row.get(
        "distance_to_facility"
    )

    if distance is None:
        return 0.0

    try:
        distance = float(
            distance
        )
    except (
        ValueError,
        TypeError
    ):
        return 0.0

    if distance <= 100:
        return 1.0

    if distance <= 250:
        return 0.85

    if distance <= 500:
        return 0.65

    if distance <= 1000:
        return 0.40

    return 0.0


def facility_type_score(
    row
) -> float:

    facility_type = str(
        row.get(
            "facility_type",
            ""
        )
    ).lower()

    if not facility_type:
        return 0.0

    strong_types = [
        "refinery",
        "chemical",
        "petrochemical",
        "oil",
        "gas",
        "power",
        "power plant",
    ]

    medium_types = [
        "industrial",
        "factory",
        "works",
        "plant",
    ]

    if any(
        value in facility_type
        for value in strong_types
    ):
        return 1.0

    if any(
        value in facility_type
        for value in medium_types
    ):
        return 0.65

    return 0.20


def industrial_evidence(
    row
) -> Dict:

    distance = facility_distance_score(
        row
    )

    facility = facility_type_score(
        row
    )

    context = industrial_context_score(
        row
    )

    score = (
        distance * 0.40
        + facility * 0.35
        + context * 0.25
    )

    reasons: List[str] = []

    if distance >= 0.85:
        reasons.append(
            "Very close to an industrial facility"
        )

    elif distance >= 0.60:
        reasons.append(
            "Near an industrial facility"
        )

    if facility >= 0.90:
        reasons.append(
            "High-priority industrial facility type"
        )

    elif facility >= 0.60:
        reasons.append(
            "Industrial facility context detected"
        )

    if context >= 0.75:
        reasons.append(
            "Strong industrial spatial context"
        )

    return {
        "score": round(
            score,
            4
        ),
        "reasons": reasons,
        "distance_score": distance,
        "facility_type_score": facility,
        "industrial_context_score": context,
    }
def classify_industrial_candidate(
    row
):

    evidence = industrial_evidence(
        row
    )

    industrial_score = (
        evidence["score"]
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

    frp = float(
        row.get(
            "frp",
            0.0
        ) or 0.0
    )

    score_flare = (
        industrial_score * 0.50
        + persistence * 0.30
        + (1.0 - anomaly) * 0.20
    )

    score_fire = (
        industrial_score * 0.35
        + anomaly * 0.40
        + min(
            frp / 300.0,
            1.0
        ) * 0.25
    )

    return {
        "industrial_score": round(
            industrial_score,
            4
        ),
        "flare_score": round(
            score_flare,
            4
        ),
        "fire_score": round(
            score_fire,
            4
        ),
        "reasons": evidence[
            "reasons"
        ],
    }