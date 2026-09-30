from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb

from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from class_weights import (
    calculate_sample_weights,
)

from model_features import (
    FEATURE_COLUMNS,
    LABELS,
    MODEL_DIR,
    MODEL_PATH,
    LABEL_ENCODER_PATH,
    METRICS_PATH,
    FEATURE_IMPORTANCE_PATH,
    CONFUSION_MATRIX_PATH,
)


BASE_DIR = (
    Path(__file__).resolve().parent
)

DATASET = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "final_training_dataset.parquet"
)


TRAIN_END_YEAR = 2024
VALIDATION_YEAR = 2025
TEST_START_YEAR = 2026


def ensure_feature_compatibility(df):

    if "forest_context" in df.columns and "tree_fraction" in df.columns:
        df["forest_context"] = df["forest_context"].fillna(df["tree_fraction"])

    if "agricultural_context" in df.columns and "cropland_fraction" in df.columns:
        df["agricultural_context"] = df["agricultural_context"].fillna(df["cropland_fraction"])

    if "builtup_context" in df.columns and "builtup_fraction" in df.columns:
        df["builtup_context"] = df["builtup_context"].fillna(df["builtup_fraction"])

    for column in [
        "forest_context",
        "agricultural_context",
        "builtup_context",
        "ndvi_mean",
        "ndvi_std",
        "ndmi_mean",
        "ndmi_std",
        "sentinel2_quality_score",
    ]:
        if column not in df.columns:
            df[column] = 0.0

    if "sentinel2_quality_score" in df.columns and "confidence_score" in df.columns:
        df["sentinel2_quality_score"] = df["sentinel2_quality_score"].fillna(df["confidence_score"])

    if "day_night_numeric" not in df.columns:
        day_column = df["day_night"] if "day_night" in df.columns else df["daynight"] if "daynight" in df.columns else pd.Series("D", index=df.index)
        day_values = day_column.fillna("D").astype(str).str.upper()
        df["day_night_numeric"] = np.where(day_values == "N", 1.0, 0.0)

    if "firms_type" not in df.columns:
        df["firms_type"] = 0

    return df


def validate_dataset(df):

    df = ensure_feature_compatibility(df)

    required = (
        FEATURE_COLUMNS
        + [
            "human_label",
            "acquired_at",
        ]
    )

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            "Missing columns: "
            + ", ".join(missing)
        )

    invalid_labels = set(
        df[
            "human_label"
        ].unique()
    ) - set(LABELS)

    if invalid_labels:

        raise ValueError(
            "Unexpected labels: "
            + ", ".join(
                map(
                    str,
                    invalid_labels
                )
            )
        )


def split_temporally(df):

    year = (
        df[
            "acquired_at"
        ]
        .dt.year
    )

    train = df[
        year <= TRAIN_END_YEAR
    ].copy()

    validation = df[
        year == VALIDATION_YEAR
    ].copy()

    test = df[
        year >= TEST_START_YEAR
    ].copy()

    return (
        train,
        validation,
        test,
    )


def print_split(
    name,
    df
):

    print()
    print(
        f"{name}: {len(df)} rows"
    )

    if len(df) == 0:

        print(
            "  WARNING: split is empty"
        )

        return

    print(
        df[
            "human_label"
        ].value_counts()
    )


def main():

    if not DATASET.exists():

        raise FileNotFoundError(
            f"Dataset missing: {DATASET}"
        )

    df = pd.read_parquet(
        DATASET
    )

    df[
        "acquired_at"
    ] = pd.to_datetime(
        df[
            "acquired_at"
        ],
        utc=True,
        errors="coerce"
    )

    df = df[
        df[
            "acquired_at"
        ].notna()
    ].copy()

    validate_dataset(
        df
    )

    train, validation, test = (
        split_temporally(
            df
        )
    )

    print(
        "=" * 60
    )

    print(
        "REAL THERMOS MODEL TRAINING"
    )

    print(
        "=" * 60
    )

    print_split(
        "TRAIN",
        train
    )

    print_split(
        "VALIDATION",
        validation
    )

    print_split(
        "TEST",
        test
    )

    if len(train) == 0:

        raise RuntimeError(
            "Training set is empty."
        )

    train_labels = (
        train["human_label"]
        .dropna()
        .astype(str)
        .str.upper()
        .str.strip()
    )

    if train_labels.nunique() == 1:

        print(
            "\nWARNING:"
            "\nTraining data contains only one class: "
            f"{train_labels.unique().tolist()}. "
            "Using a fallback majority-class model for this dataset."
        )

    if len(validation) == 0:

        print(
            "\nWARNING:"
            "\nValidation set is empty."
            "\nAcquire a later time period."
        )

    if len(test) == 0:

        print(
            "\nWARNING:"
            "\nTest set is empty."
            "\nAcquire 2026 data before "
            "claiming final test performance."
        )

    # -------------------------
    # Feature matrices
    # -------------------------

    X_train = train[
        FEATURE_COLUMNS
    ].copy()

    X_validation = validation[
        FEATURE_COLUMNS
    ].copy()

    X_test = test[
        FEATURE_COLUMNS
    ].copy()

    # Numeric coercion.
    for column in FEATURE_COLUMNS:

        X_train[column] = pd.to_numeric(
            X_train[column],
            errors="coerce"
        )

        X_validation[column] = (
            pd.to_numeric(
                X_validation[column],
                errors="coerce"
            )
        )

        X_test[column] = pd.to_numeric(
            X_test[column],
            errors="coerce"
        )

    # Fit imputer ONLY on training data.
    imputer = SimpleImputer(
        strategy="median"
    )

    X_train = imputer.fit_transform(
        X_train
    )

    if len(validation) > 0:
        X_validation = imputer.transform(
            X_validation
        )
    else:
        X_validation = np.empty(
            (0, X_train.shape[1]),
            dtype=float,
        )

    if len(test) > 0:
        X_test = imputer.transform(
            X_test
        )
    else:
        X_test = np.empty(
            (0, X_train.shape[1]),
            dtype=float,
        )

    # -------------------------
    # Labels
    # -------------------------

    encoder = LabelEncoder()

    encoder.fit(
        train_labels.unique()
    )

    y_train = encoder.transform(
        train[
            "human_label"
        ]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    if len(validation) > 0:
        y_validation = encoder.transform(
            validation[
                "human_label"
            ]
        )
    else:
        y_validation = np.array(
            [],
            dtype=int,
        )

    if len(test) > 0:
        y_test = encoder.transform(
            test[
                "human_label"
            ]
        )
    else:
        y_test = np.array(
            [],
            dtype=int,
        )

    # -------------------------
    # Class balancing
    # -------------------------

    sample_weights = (
        calculate_sample_weights(
            y_train
        )
    )

    # -------------------------
    # Model
    # -------------------------

    if train_labels.nunique() == 1:

        model = DummyClassifier(
            strategy="most_frequent"
        )
        model.fit(
            X_train,
            y_train,
        )

    else:

        model = xgb.XGBClassifier(

            objective="multi:softprob",

            num_class=len(
                encoder.classes_
            ),

            n_estimators=500,

            max_depth=7,

            learning_rate=0.04,

            min_child_weight=3,

            subsample=0.85,

            colsample_bytree=0.85,

            reg_alpha=0.1,

            reg_lambda=1.0,

            eval_metric="mlogloss",

            tree_method="hist",

            random_state=42,

            n_jobs=-1,
        )

        fit_kwargs = {
            "sample_weight": sample_weights,
        }

        if len(validation) > 0:

            fit_kwargs[
                "eval_set"
            ] = [
                (
                    X_validation,
                    y_validation
                )
            ]

            fit_kwargs[
                "verbose"
            ] = True

        model.fit(
            X_train,
            y_train,
            **fit_kwargs
        )

    # -------------------------
    # Save model
    # -------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if hasattr(model, "save_model"):
        model.save_model(
            MODEL_PATH
        )
    else:
        joblib.dump(
            model,
            MODEL_DIR
            / "thermal_classifier.joblib"
        )

    joblib.dump(
        encoder,
        LABEL_ENCODER_PATH
    )

    joblib.dump(
        imputer,
        MODEL_DIR
        / "feature_imputer.joblib"
    )

    # -------------------------
    # Evaluation helper
    # -------------------------

    def evaluate(
        split_name,
        X,
        y
    ):

        if len(y) == 0:

            return None

        predictions = model.predict(
            X
        )

        probabilities = (
            model.predict_proba(
                X
            )
        )

        accuracy = (
            accuracy_score(
                y,
                predictions
            )
        )

        balanced_accuracy = (
            balanced_accuracy_score(
                y,
                predictions
            )
        )

        precision = (
            precision_score(
                y,
                predictions,
                average="weighted",
                zero_division=0
            )
        )

        recall = (
            recall_score(
                y,
                predictions,
                average="weighted",
                zero_division=0
            )
        )

        f1 = (
            f1_score(
                y,
                predictions,
                average="weighted",
                zero_division=0
            )
        )

        report = classification_report(
            y,
            predictions,
            labels=np.arange(
                len(encoder.classes_)
            ),
            target_names=encoder.classes_.tolist(),
            output_dict=True,
            zero_division=0,
        )

        matrix = confusion_matrix(
            y,
            predictions,
            labels=np.arange(
                len(encoder.classes_)
            )
        )

        return {
            "split": split_name,

            "rows": len(y),

            "accuracy": float(
                accuracy
            ),

            "balanced_accuracy":
                float(
                    balanced_accuracy
                ),

            "weighted_precision":
                float(
                    precision
                ),

            "weighted_recall":
                float(
                    recall
                ),

            "weighted_f1":
                float(
                    f1
                ),

            "classification_report":
                report,

            "confusion_matrix":
                matrix.tolist(),
        }

    validation_metrics = evaluate(
        "validation",
        X_validation,
        y_validation
    )

    test_metrics = evaluate(
        "test",
        X_test,
        y_test
    )

    # -------------------------
    # Feature importance
    # -------------------------

    if hasattr(model, "feature_importances_"):
        importance = (
            pd.DataFrame(
                {
                    "feature":
                        FEATURE_COLUMNS,

                    "importance":
                        model.feature_importances_,
                }
            )
            .sort_values(
                "importance",
                ascending=False
            )
        )
    else:
        importance = pd.DataFrame(
            {
                "feature": FEATURE_COLUMNS,
                "importance": [0.0] * len(FEATURE_COLUMNS),
            }
        )

    importance.to_csv(
        FEATURE_IMPORTANCE_PATH,
        index=False
    )

    # -------------------------
    # Save metrics
    # -------------------------

    metrics = {
        "dataset": str(
            DATASET
        ),

        "features":
            FEATURE_COLUMNS,

        "classes":
            LABELS,

        "train_rows":
            len(train),

        "validation_rows":
            len(validation),

        "test_rows":
            len(test),

        "validation":
            validation_metrics,

        "test":
            test_metrics,
    }

    with open(
        METRICS_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metrics,
            file,
            indent=2
        )

    if test_metrics:

        pd.DataFrame(
            test_metrics[
                "confusion_matrix"
            ],
            index=encoder.classes_.tolist(),
            columns=encoder.classes_.tolist()
        ).to_csv(
            CONFUSION_MATRIX_PATH
        )

    print()
    print(
        "=" * 60
    )

    print(
        "TRAINING COMPLETE"
    )

    print(
        "=" * 60
    )

    print(
        f"Model: {MODEL_PATH}"
    )

    print(
        f"Encoder: {LABEL_ENCODER_PATH}"
    )

    print(
        f"Metrics: {METRICS_PATH}"
    )

    print(
        f"Feature importance: "
        f"{FEATURE_IMPORTANCE_PATH}"
    )

    if test_metrics:

        print()
        print(
            "TEST RESULTS"
        )

        print(
            f"Accuracy: "
            f"{test_metrics['accuracy']:.4f}"
        )

        print(
            "Balanced accuracy: "
            f"{test_metrics['balanced_accuracy']:.4f}"
        )

        print(
            "Weighted F1: "
            f"{test_metrics['weighted_f1']:.4f}"
        )


if __name__ == "__main__":
    main()