import numpy as np


def safe_normalized_difference(
    numerator_a,
    numerator_b
):

    denominator = (
        numerator_a
        + numerator_b
    )

    return np.divide(
        numerator_a - numerator_b,
        denominator,
        out=np.zeros_like(
            denominator,
            dtype=np.float32
        ),
        where=denominator != 0
    )


def calculate_ndvi(
    red,
    nir
):

    return safe_normalized_difference(
        nir,
        red
    )


def calculate_ndmi(
    nir,
    swir
):

    return safe_normalized_difference(
        nir,
        swir
    )


def summarize_index(
    index
):

    valid = index[
        np.isfinite(index)
    ]

    if valid.size == 0:

        return {
            "mean": 0.0,
            "std": 0.0,
            "min": 0.0,
            "max": 0.0,
        }

    return {
        "mean": float(
            np.mean(valid)
        ),
        "std": float(
            np.std(valid)
        ),
        "min": float(
            np.min(valid)
        ),
        "max": float(
            np.max(valid)
        ),
    }