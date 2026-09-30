from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb

from sklearn.impute import SimpleImputer

from metrics import (
    calculate_metrics
)

from error_analysis import (
    build_error_table,
    save_errors,
)

from model_features import (
    FEATURE_COLUMNS,
    LABELS,
    MODEL_PATH,
    LABEL_ENCODER_PATH,
)


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parents[1]
)

DATASET = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "final_training_dataset.parquet"
)

MODEL_DIR = (
    BASE_DIR
    / "models"
)

IMPUTER_PATH = (
    MODEL_DIR
    / "feature_imputer.joblib"
)

OUTPUT_METRICS = (
    MODEL_DIR
    / "validation_metrics.json"
)

OUTPUT_ERRORS = (
    MODEL_DIR
    / "prediction_errors.parquet"
)


def load_model():

    model = xgb.XGBClassifier()

    model.load_model(
        MODEL_PATH
    )

    encoder = joblib.load(
        LABEL_ENCODER_PATH
    )

    imputer = joblib.load(
        IMPUTER_PATH
    )

    return (
        model,
        encoder,
        imputer,
    )


def prepare_matrix(
    frame,
    imputer
):

    X = frame[
        FEATURE_COLUMNS
    ].copy()

    for column in FEATURE_COLUMNS:

        X[column] = pd.to_numeric(
            X[column],
            errors="coerce"
        )

    return imputer.transform(
        X
    )


def main():

    if not DATASET.exists():

        raise FileNotFoundError(
            DATASET
        )

    model, encoder, imputer = (
        load_model()
    )

    df = pd.read_parquet(
        DATASET
    )

    df[
        "acquired_at"
    ] = pd.to_datetime(
        df["acquired_at"],
        utc=True,
        errors="coerce"
    )

    df = df[
        df["acquired_at"].notna()
    ].copy()

    test = df[
        df["acquired_at"].dt.year >= 2026
    ].copy()

    if test.empty:

        print(
            "=" * 60
        )

        print(
            "NO 2026 TEST SET AVAILABLE"
        )

        print(
            "=" * 60
        )

        print(
            "Do NOT claim final test metrics."
        )

        print(
            "Acquire a genuinely held-out "
            "later period first."
        )

        return

    X_test = prepare_matrix(
        test,
        imputer
    )

    y_test = encoder.transform(
        test["human_label"]
    )

    predictions = model.predict(
        X_test
    )

    probabilities = (
        model.predict_proba(
            X_test
        )
    )

    label_indices = np.arange(
        len(LABELS)
    )

    metrics = calculate_metrics(
        y_true=y_test,
        y_pred=predictions,
        labels=label_indices,
        label_names=LABELS,
    )

    errors = build_error_table(
        dataframe=test,
        y_true=y_test,
        y_pred=predictions,
        probabilities=probabilities,
        label_encoder=encoder,
    )

    save_errors(
        errors,
        OUTPUT_ERRORS
    )

    with open(
        OUTPUT_METRICS,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metrics,
            file,
            indent=2
        )

    print()
    print(
        "=" * 60
    )

    print(
        "HELD-OUT TEST EVALUATION"
    )

    print(
        "=" * 60
    )

    print(
        f"Test rows: {len(test)}"
    )

    print(
        f"Accuracy: "
        f"{metrics['accuracy']:.4f}"
    )

    print(
        "Balanced accuracy: "
        f"{metrics['balanced_accuracy']:.4f}"
    )

    print(
        "Macro F1: "
        f"{metrics['macro_f1']:.4f}"
    )

    print(
        "Weighted F1: "
        f"{metrics['weighted_f1']:.4f}"
    )

    print(
        f"\nMetrics: {OUTPUT_METRICS}"
    )

    print(
        f"Errors: {OUTPUT_ERRORS}"
    )


if __name__ == "__main__":
    main()