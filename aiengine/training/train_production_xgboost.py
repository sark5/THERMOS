from pathlib import Path
import json

import joblib
import pandas as pd
import xgboost as xgb

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import (
    compute_sample_weight,
)
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    balanced_accuracy_score,
    f1_score,
)


BASE_DIR = (
    Path(__file__).resolve().parent
)

DATASET = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "production_labeled.parquet"
)

MODEL_DIR = (
    BASE_DIR
    / "models"
)

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

FEATURES = [
    "frp",
    "bright_ti4",
    "bright_ti5",
    "confidence_score",
    "day_night_numeric",
    "firms_type",

    "persistence_score",
    "stability_score",
    "anomaly_score",
    "frp_spike_score",
    "periodicity_score",
    "spatial_spread_score",
    "temporal_growth_score",

    "distance_to_facility",
    "industrial_context",
    "forest_context",
    "agricultural_context",
    "builtup_context",
    "mining_context",
    "bare_land_context",
    "spatial_clustering_score",

    "ndvi_mean",
    "ndvi_std",
    "ndmi_mean",
    "ndmi_std",
    "sentinel2_quality_score",
]


CLASSES = [
    "INDUSTRIAL_FLARE",
    "INDUSTRIAL_FIRE",
    "MINING",
    "AGRICULTURAL",
    "WILDFIRE",
    "UNCLASSIFIED",
]


def prepare_frame(
    frame
):

    frame = frame.copy()

    frame[
        "acquired_at"
    ] = pd.to_datetime(
        frame[
            "acquired_at"
        ],
        utc=True,
        errors="coerce"
    )

    frame = frame[
        frame["acquired_at"].notna()
    ].copy()

    # Only sufficiently reliable pseudo-labels.
    frame = frame[
        frame[
            "label_quality"
        ].isin(
            [
                "STRONG",
                "MODERATE",
            ]
        )
    ].copy()

    frame = frame[
        frame[
            "thermos_label"
        ].isin(
            CLASSES
        )
    ].copy()

    return frame


def main():

    df = pd.read_parquet(
        DATASET
    )

    df = prepare_frame(
        df
    )

    print(
        f"Training candidates: {len(df)}"
    )

    train = df[
        df["acquired_at"].dt.year
        <= 2023
    ].copy()

    calibration = df[
        df["acquired_at"].dt.year
        == 2024
    ].copy()

    validation = df[
        df["acquired_at"].dt.year
        == 2025
    ].copy()

    test = df[
        df["acquired_at"].dt.year
        >= 2026
    ].copy()

    print(
        f"Train: {len(train)}"
    )

    print(
        f"Calibration: {len(calibration)}"
    )

    print(
        f"Validation: {len(validation)}"
    )

    print(
        f"Test: {len(test)}"
    )

    X_train = train[
        FEATURES
    ].copy()

    X_validation = validation[
        FEATURES
    ].copy()

    X_test = test[
        FEATURES
    ].copy()

    for column in FEATURES:

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

    # Fit preprocessing only on TRAIN.
    imputer = SimpleImputer(
        strategy="median"
    )

    X_train = imputer.fit_transform(
        X_train
    )

    X_validation = imputer.transform(
        X_validation
    )

    X_test = imputer.transform(
        X_test
    )

    encoder = LabelEncoder()

    encoder.fit(
        CLASSES
    )

    y_train = encoder.transform(
        train[
            "thermos_label"
        ]
    )

    y_validation = encoder.transform(
        validation[
            "thermos_label"
        ]
    )

    y_test = encoder.transform(
        test[
            "thermos_label"
        ]
    )

    weights = (
        compute_sample_weight(
            class_weight="balanced",
            y=y_train
        )
    )

    model = xgb.XGBClassifier(
        objective="multi:softprob",
        num_class=len(
            CLASSES
        ),
        n_estimators=700,
        max_depth=8,
        learning_rate=0.035,
        min_child_weight=4,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_alpha=0.2,
        reg_lambda=1.5,
        eval_metric="mlogloss",
        tree_method="hist",
        n_jobs=-1,
        random_state=42,
    )

    model.fit(
        X_train,
        y_train,
        sample_weight=weights,
        eval_set=[
            (
                X_validation,
                y_validation
            )
        ],
        verbose=True
    )

    model_path = (
        MODEL_DIR
        / "thermos_xgboost_real.json"
    )

    model.save_model(
        model_path
    )

    joblib.dump(
        encoder,
        MODEL_DIR
        / "thermos_label_encoder.joblib"
    )

    joblib.dump(
        imputer,
        MODEL_DIR
        / "thermos_feature_imputer.joblib"
    )

    # Evaluation.
    predictions = model.predict(
        X_test
    )

    report = classification_report(
        y_test,
        predictions,
        labels=range(
            len(CLASSES)
        ),
        target_names=CLASSES,
        output_dict=True,
        zero_division=0,
    )

    metrics = {
        "train_rows": len(train),
        "calibration_rows":
            len(calibration),
        "validation_rows":
            len(validation),
        "test_rows": len(test),

        "balanced_accuracy":
            float(
                balanced_accuracy_score(
                    y_test,
                    predictions
                )
            ),

        "macro_f1":
            float(
                f1_score(
                    y_test,
                    predictions,
                    average="macro",
                    zero_division=0
                )
            ),

        "classification_report":
            report,

        "confusion_matrix":
            confusion_matrix(
                y_test,
                predictions,
                labels=range(
                    len(CLASSES)
                )
            ).tolist()
    }

    with open(
        MODEL_DIR
        / "real_model_metrics.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metrics,
            file,
            indent=2
        )

    importance = pd.DataFrame(
        {
            "feature": FEATURES,
            "importance":
                model.feature_importances_,
        }
    ).sort_values(
        "importance",
        ascending=False
    )

    importance.to_csv(
        MODEL_DIR
        / "real_feature_importance.csv",
        index=False
    )

    print()
    print(
        "=" * 70
    )

    print(
        "REAL THERMOS MODEL COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        f"Model: {model_path}"
    )

    print(
        f"Macro F1: "
        f"{metrics['macro_f1']:.4f}"
    )

    print(
        "Balanced accuracy: "
        f"{metrics['balanced_accuracy']:.4f}"
    )


if __name__ == "__main__":
    main()