from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.metrics import (
    log_loss,
    brier_score_loss,
)


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
)

MODEL_DIR = (
    BASE_DIR
    / "models"
)

DATA_DIR = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "splits"
)

CALIBRATED_MODEL = (
    MODEL_DIR
    / "thermal_classifier_calibrated.joblib"
)

ENCODER = (
    MODEL_DIR
    / "label_encoder.joblib"
)

IMPUTER = (
    MODEL_DIR
    / "feature_imputer.joblib"
)


def main():

    model = joblib.load(
        CALIBRATED_MODEL
    )

    encoder = joblib.load(
        ENCODER
    )

    imputer = joblib.load(
        IMPUTER
    )

    data = pd.read_parquet(
        DATA_DIR / "validation.parquet"
    )

    X = data[
        [
            # Keep exact feature ordering.
        ]
    ]