import numpy as np

from sklearn.utils.class_weight import (
    compute_sample_weight,
)


def calculate_sample_weights(
    labels
):

    return compute_sample_weight(
        class_weight="balanced",
        y=labels
    )