from pathlib import Path
import json

import joblib
import pandas as pd
import xgboost as xgb

from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import (
    compute_sample_weight,
)

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from final_features import (
    FEATURES,
    CLASSES,
)


BASE_DIR = (
    Path(__file__).resolve().parent
)

SPLIT_DIR = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "final_splits"
)

MODEL_DIR = (
    BASE_DIR
    / "models"
)

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def load_split(
    name
):

    path = (
        SPLIT_DIR
        / f"{name}.parquet"
    )

    if not path.exists():

        raise FileNotFoundError(
            path
        )

    return pd.read_parquet(
        path
    )


def prepare_X(
    df,
    imputer=None,
    fit=False
):

    X = df[
        FEATURES
    ].copy()

    for column in FEATURES:

        X[column] = pd.to_numeric(
            X[column],
            errors="coerce"
        )

    if fit:

        X = imputer.fit_transform(
            X
        )

    else:

        X = imputer.transform(
            X
        )

    return X


def main():

    train = load_split(
        "train"
    )

    validation = load_split(
        "validation"
    )

    test = load_split(
        "test"
    )

    print(
        "=" * 70
    )

    print(
        "FINAL REAL-DATA XGBOOST TRAINING"
    )

    print(
        "=" * 70
    )

    print(
        f"Train:      {len(train)}"
    )

    print(
        f"Validation: {len(validation)}"
    )

    print(
        f"Test:       {len(test)}"
    )

    if train.empty:

        raise RuntimeError(
            "Training dataset is empty after split generation. "
            "Generate a train split first or add more labeled rows."
        )

    # ---------------------------------
    # Label encoder
    # ---------------------------------

    encoder = LabelEncoder()
    encoder.fit(train["gold_label"])

    y_train = encoder.transform(train["gold_label"])

    val_clean = validation[validation["gold_label"].isin(encoder.classes_)].copy() if not validation.empty else pd.DataFrame()
    y_validation = encoder.transform(val_clean["gold_label"]) if not val_clean.empty else None

    test_clean = test[test["gold_label"].isin(encoder.classes_)].copy() if not test.empty else pd.DataFrame()
    y_test = encoder.transform(test_clean["gold_label"]) if not test_clean.empty else None

    # ---------------------------------
    # Imputer fitted ONLY on training.
    # ---------------------------------

    imputer = SimpleImputer(
        strategy="median"
    )

    X_train = prepare_X(
        train,
        imputer,
        fit=True
    )

    X_validation = (
        prepare_X(
            val_clean,
            imputer,
            fit=False
        )
        if not val_clean.empty
        else None
    )

    X_test = (
        prepare_X(
            test_clean,
            imputer,
            fit=False
        )
        if not test_clean.empty
        else None
    )

    # ---------------------------------
    # Class balancing.
    # ---------------------------------

    sample_weights = (
        compute_sample_weight(
            class_weight="balanced",
            y=y_train
        )
    )

    # ---------------------------------
    # XGBoost
    # ---------------------------------

    model_path = (
        MODEL_DIR
        / "thermos_xgboost_final.json"
    )

    unique_labels = pd.Series(y_train).unique()

    if len(unique_labels) < 2:

        print(
            "WARNING: only one class is present in the training data; "
            "falling back to a majority-class baseline model."
        )

        model = DummyClassifier(
            strategy="most_frequent"
        )
        model.fit(
            X_train,
            y_train
        )

        with open(
            model_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                {
                    "model": "DummyClassifier",
                    "strategy": "most_frequent",
                    "classes": [
                        int(value)
                        for value in sorted(
                            unique_labels.tolist()
                        )
                    ],
                },
                file,
                indent=2,
            )

    else:

        model = xgb.XGBClassifier(
            objective="multi:softprob",

            num_class=len(
                encoder.classes_
            ),

            n_estimators=800,

            max_depth=7,

            learning_rate=0.035,

            min_child_weight=4,

            subsample=0.85,

            colsample_bytree=0.85,

            reg_alpha=0.20,

            reg_lambda=1.50,

            gamma=0.05,

            eval_metric="mlogloss",

            tree_method="hist",

            random_state=42,

            n_jobs=-1,
        )

        eval_set = []

        if X_validation is not None:

            eval_set.append(
                (
                    X_validation,
                    y_validation
                )
            )

        model.fit(
            X_train,
            y_train,

            sample_weight=
                sample_weights,

            eval_set=
                eval_set,

            verbose=True
        )

        model.save_model(
            model_path
        )
        model.save_model(
            MODEL_DIR / "thermal_classifier.json"
        )

    # ---------------------------------
    # Save preprocessing.
    # ---------------------------------

    joblib.dump(
        imputer,
        MODEL_DIR
        / "thermos_feature_imputer.joblib"
    )
    joblib.dump(
        imputer,
        MODEL_DIR
        / "feature_imputer.joblib"
    )

    joblib.dump(
        encoder,
        MODEL_DIR
        / "thermos_label_encoder.joblib"
    )
    joblib.dump(
        encoder,
        MODEL_DIR
        / "label_encoder.joblib"
    )

    # ---------------------------------
    # Validation evaluation.
    # ---------------------------------

    validation_metrics = None

    if (
        X_validation is not None
        and y_validation is not None
        and len(y_validation) > 0
    ):

        validation_predictions = (
            model.predict(
                X_validation
            )
        )

        validation_metrics = {
            "accuracy":
                float(
                    accuracy_score(
                        y_validation,
                        validation_predictions
                    )
                ),

            "balanced_accuracy":
                float(
                    balanced_accuracy_score(
                        y_validation,
                        validation_predictions
                    )
                ),

            "macro_f1":
                float(
                    f1_score(
                        y_validation,
                        validation_predictions,
                        average="macro",
                        zero_division=0
                    )
                ),

            "weighted_f1":
                float(
                    f1_score(
                        y_validation,
                        validation_predictions,
                        average="weighted",
                        zero_division=0
                    )
                ),

            "classification_report":
                classification_report(
                    y_validation,
                    validation_predictions,
                    labels=range(
                        len(CLASSES)
                    ),
                    target_names=CLASSES,
                    output_dict=True,
                    zero_division=0
                ),
        }

    # ---------------------------------
    # FINAL TEST
    # ---------------------------------

    test_metrics = None

    if (
        X_test is not None
        and y_test is not None
        and len(y_test) > 0
    ):

        test_predictions = (
            model.predict(
                X_test
            )
        )

        test_metrics = {

            "accuracy":
                float(
                    accuracy_score(
                        y_test,
                        test_predictions
                    )
                ),

            "balanced_accuracy":
                float(
                    balanced_accuracy_score(
                        y_test,
                        test_predictions
                    )
                ),

            "macro_precision":
                float(
                    precision_score(
                        y_test,
                        test_predictions,
                        average="macro",
                        zero_division=0
                    )
                ),

            "macro_recall":
                float(
                    recall_score(
                        y_test,
                        test_predictions,
                        average="macro",
                        zero_division=0
                    )
                ),

            "macro_f1":
                float(
                    f1_score(
                        y_test,
                        test_predictions,
                        average="macro",
                        zero_division=0
                    )
                ),

            "weighted_f1":
                float(
                    f1_score(
                        y_test,
                        test_predictions,
                        average="weighted",
                        zero_division=0
                    )
                ),

            "classification_report":
                classification_report(
                    y_test,
                    test_predictions,
                    labels=range(
                        len(CLASSES)
                    ),
                    target_names=CLASSES,
                    output_dict=True,
                    zero_division=0
                ),

            "confusion_matrix":
                confusion_matrix(
                    y_test,
                    test_predictions,
                    labels=range(
                        len(CLASSES)
                    )
                ).tolist(),
        }

        pd.DataFrame(
            test_metrics[
                "confusion_matrix"
            ],
            index=CLASSES,
            columns=CLASSES
        ).to_csv(
            MODEL_DIR
            / "final_confusion_matrix.csv"
        )

    # ---------------------------------
    # Feature importance.
    # ---------------------------------

    importance_values = (
        model.feature_importances_
        if hasattr(
            model,
            "feature_importances_"
        )
        else [0.0] * len(FEATURES)
    )

    importance = (
        pd.DataFrame(
            {
                "feature":
                    FEATURES,

                "importance":
                    importance_values,
            }
        )
        .sort_values(
            "importance",
            ascending=False
        )
    )

    importance.to_csv(
        MODEL_DIR
        / "final_feature_importance.csv",
        index=False
    )

    # ---------------------------------
    # Save complete run metadata.
    # ---------------------------------

    metrics = {
        "model": "XGBoost",

        "features":
            FEATURES,

        "classes":
            CLASSES,

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
        MODEL_DIR
        / "final_training_metrics.json",
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
        "=" * 70
    )

    print(
        "MODEL TRAINING FINISHED"
    )

    print(
        "=" * 70
    )

    print(
        f"Model:\n{model_path}"
    )

    if validation_metrics:

        print(
            "\nVALIDATION"
        )

        print(
            f"Balanced accuracy: "
            f"{validation_metrics['balanced_accuracy']:.4f}"
        )

        print(
            f"Macro F1: "
            f"{validation_metrics['macro_f1']:.4f}"
        )

    if test_metrics:

        print(
            "\nFINAL TEST"
        )

        print(
            f"Balanced accuracy: "
            f"{test_metrics['balanced_accuracy']:.4f}"
        )

        print(
            f"Macro F1: "
            f"{test_metrics['macro_f1']:.4f}"
        )

    else:

        print(
            "\nNo valid 2026 test rows available."
        )


if __name__ == "__main__":
    main()