import numpy as np
import pandas as pd

from model_features import (
    FEATURE_COLUMNS,
)


def prepare_features(df):

    df = df.copy()

    missing = [
        column
        for column in FEATURE_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Missing required model features: "
            + ", ".join(missing)
        )

    X = df[
        FEATURE_COLUMNS
    ].copy()

    for column in FEATURE_COLUMNS:

        X[column] = pd.to_numeric(
            X[column],
            errors="coerce"
        )

    # Controlled imputation.
    #
    # Median imputation is calculated from
    # the training dataframe only by the
    # training script.
    #
    # This function just returns the numeric
    # matrix.
    return X 