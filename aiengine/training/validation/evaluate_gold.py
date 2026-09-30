from pathlib import Path
import json

import joblib
import pandas as pd
import xgboost as xgb

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    balanced_accuracy_score,
    f1_score,
    precision_score,
    recall_score,
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

GOLD_DATASET = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "gold_dataset.parquet"
)

IMPUTER_PATH = (
    BASE_DIR
    / "models"
    / "feature_imputer.joblib"
)

OUTPUT = (
    BASE_DIR
    / "models"
    / "gold_metrics.json"
)


def main():

    if not GOLD_DATASET.exists():

        raise FileNotFoundError(
            GOLD_DATASET
        )

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

    df = pd.read_parquet(
        GOLD_DATASET
    )

    if "human_label" not in df.columns:

        raise ValueError(
            "human_label missing from gold dataset."
        )

    df[
        "human_label"
    ] = (
        df[
            "human_label"
        ]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    df = df[
        df["human_label"].isin(
            LABELS
        )
    ].copy()

    X = df[
        FEATURE_COLUMNS
    ].copy()

    for column in FEATURE_COLUMNS:

        X[column] = pd.to_numeric(
            X[column],
            errors="coerce"
        )

    X = imputer.transform(
        X
    )

    y = encoder.transform(
        df["human_label"]
    )

    predictions = model.predict(
        X
    )

    report = classification_report(
        y,
        predictions,
        labels=range(
            len(LABELS)
        ),
        target_names=LABELS,
        output_dict=True,
        zero_division=0,
    )

    metrics = {
        "rows": len(df),

        "balanced_accuracy":
            float(
                balanced_accuracy_score(
                    y,
                    predictions
                )
            ),

        "macro_precision":
            float(
                precision_score(
                    y,
                    predictions,
                    average="macro",
                    zero_division=0
                )
            ),

        "macro_recall":
            float(
                recall_score(
                    y,
                    predictions,
                    average="macro",
                    zero_division=0
                )
            ),

        "macro_f1":
            float(
                f1_score(
                    y,
                    predictions,
                    average="macro",
                    zero_division=0
                )
            ),

        "classification_report":
            report,

        "confusion_matrix":
            confusion_matrix(
                y,
                predictions,
                labels=range(
                    len(LABELS)
                )
            ).tolist(),
    }

    with open(
        OUTPUT,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metrics,
            file,
            indent=2
        )

    print(
        "=" * 60
    )

    print(
        "GOLD DATASET EVALUATION"
    )

    print(
        "=" * 60
    )

    print(
        f"Rows: {len(df)}"
    )

    print(
        f"Balanced accuracy: "
        f"{metrics['balanced_accuracy']:.4f}"
    )

    print(
        f"Macro F1: "
        f"{metrics['macro_f1']:.4f}"
    )

    print(
        f"Saved: {OUTPUT}"
    )


if __name__ == "__main__":
    main()