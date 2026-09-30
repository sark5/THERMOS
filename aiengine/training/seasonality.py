import numpy as np


def circular_month_distance(
    month_a,
    month_b
):

    difference = abs(
        month_a  
        - month_b
    )

    return min(
        difference,
        12 - difference
    )


def seasonality_score(
    historical_months,
    current_month
):

    if not historical_months:
        return 0.0

    matches = 0

    for month in historical_months:

        distance = (
            circular_month_distance(
                month,
                current_month
            )
        )

        if distance <= 1:
            matches += 1

    score = (
        matches
        / len(historical_months)
    )

    return round(
        min(
            score,
            1.0
        ),
        4
    )