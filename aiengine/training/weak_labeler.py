from rules.industrial_rules import (
    classify_industrial_candidate,
)

from rules.mining_rules import (
    mining_evidence,
)

from rules.agricultural_rules import (
    agricultural_evidence,
)

from rules.wildfire_rules import (
    wildfire_evidence,
)


def quality_from_score(
    score
):

    if score >= 0.85:
        return "STRONG"

    if score >= 0.65:
        return "MODERATE"

    if score >= 0.45:
        return "WEAK"

    return "UNRESOLVED"


def generate_weak_label(
    row
):

    candidates = []

    industrial = (
        classify_industrial_candidate(
            row
        )
    )

    mining = mining_evidence(
        row
    )

    agricultural = (
        agricultural_evidence(
            row
        )
    )

    wildfire = wildfire_evidence(
        row
    )

    candidates.append(
        (
            "INDUSTRIAL_FLARE",
            industrial["flare_score"],
            industrial["reasons"],
        )
    )

    candidates.append(
        (
            "INDUSTRIAL_FIRE",
            industrial["fire_score"],
            industrial["reasons"],
        )
    )

    candidates.append(
        (
            "MINING",
            mining["score"],
            mining["reasons"],
        )
    )

    candidates.append(
        (
            "AGRICULTURAL",
            agricultural["score"],
            agricultural["reasons"],
        )
    )

    candidates.append(
        (
            "WILDFIRE",
            wildfire["score"],
            wildfire["reasons"],
        )
    )

    candidates.sort(
        key=lambda value: value[1],
        reverse=True
    )

    best_label = candidates[0]

    second_label = (
        candidates[1]
    )

    label = best_label[0]
    score = float(
        best_label[1]
    )

    margin = (
        score
        - float(second_label[1])
    )

    # Require both a reasonable
    # absolute score and separation
    # from the second candidate.
    if (
        score < 0.60
        or margin < 0.10
    ):

        label = "UNCLASSIFIED"
        quality = "UNRESOLVED"

    else:

        quality = quality_from_score(
            score
        )

    return {
        "thermos_label": label,
        "label_score": round(
            score,
            4
        ),
        "label_quality": quality,
        "runner_up_label": (
            second_label[0]
        ),
        "runner_up_score": round(
            float(second_label[1]),
            4
        ),
        "label_margin": round(
            margin,
            4
        ),
        "label_reasons": (
            best_label[2]
        ),
    }