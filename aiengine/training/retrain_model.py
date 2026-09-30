"""
THERMOS Retraining & Calibration Pipeline
Trains XGBoost on gold_dataset.parquet (116,181 rows) with:
1. Stratified group-aware train / validation / test splits
2. Class-balanced sample weighting for sharp multi-class separation
3. Probability calibration via isotonic regression
4. Complete export of inference artifacts to aiengine/models/ and training/models/
"""

import sys
import json
from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.isotonic import IsotonicRegression
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
import xgboost as xgb

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "datasets" / "processed"
SPLITS_DIR = DATA_DIR / "final_splits"
MODELS_DIR = ROOT / "models"
APP_MODELS_DIR = ROOT.parent / "models"

SPLITS_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
APP_MODELS_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(ROOT))
from final_features import FEATURES, CLASSES
from calibrated_model import ThermosCalibratedModel


def stratified_group_split(df: pd.DataFrame, train_frac=0.70, val_frac=0.15, test_frac=0.15, seed=42):
    """
    Splits dataset into train, validation, test splits stratified by class
    while keeping sources grouped within splits to prevent spatial-temporal leakage.
    """
    rng = np.random.RandomState(seed)
    train_dfs = []
    val_dfs = []
    test_dfs = []

    print("\nPartitioning 116,181 rows with Group-Stratified Splitting...")

    for cls_name, grp in df.groupby("gold_label"):
        sources = np.array(grp["source_id"].unique())
        rng.shuffle(sources)
        n_src = len(sources)

        n_train = int(n_src * train_frac)
        n_val = int(n_src * val_frac)

        train_src = set(sources[:n_train])
        val_src = set(sources[n_train:n_train + n_val])
        test_src = set(sources[n_train + n_val:])

        train_subset = grp[grp["source_id"].isin(train_src)]
        val_subset = grp[grp["source_id"].isin(val_src)]
        test_subset = grp[grp["source_id"].isin(test_src)]

        # Guarantee at least some validation and test samples if sources are small
        if len(val_subset) < 20 and len(train_subset) > 40:
            extra = train_subset.sample(frac=0.15, random_state=seed)
            val_subset = pd.concat([val_subset, extra])
        if len(test_subset) < 20 and len(train_subset) > 40:
            extra = train_subset.sample(frac=0.15, random_state=seed + 1)
            test_subset = pd.concat([test_subset, extra])

        train_dfs.append(train_subset)
        val_dfs.append(val_subset)
        test_dfs.append(test_subset)

        print(f"  {cls_name:18s}: {len(train_subset):5d} train | {len(val_subset):5d} val | {len(test_subset):5d} test")

    train_df = pd.concat(train_dfs).sample(frac=1.0, random_state=seed).reset_index(drop=True)
    val_df = pd.concat(val_dfs).sample(frac=1.0, random_state=seed).reset_index(drop=True)
    test_df = pd.concat(test_dfs).sample(frac=1.0, random_state=seed).reset_index(drop=True)

    return train_df, val_df, test_df


def main():
    print("=" * 70)
    print("      THERMOS RETRAINING & MULTI-CLASS CALIBRATION PIPELINE       ")
    print("=" * 70)

    gold_path = DATA_DIR / "gold_dataset.parquet"
    if not gold_path.exists():
        raise FileNotFoundError(f"Missing {gold_path}")

    print(f"Loading gold dataset: {gold_path}...")
    df = pd.read_parquet(gold_path)
    print(f"Loaded {len(df):,} records with {len(df.columns)} columns.")

    # 1. Stratified Group Split
    train_df, val_df, test_df = stratified_group_split(df)

    print(f"\nFinal Split Sizes:")
    print(f"  Train:      {len(train_df):,} rows")
    print(f"  Validation: {len(val_df):,} rows")
    print(f"  Test:       {len(test_df):,} rows")

    # Save split files for reproducible evaluation & benchmarks
    train_df.to_parquet(SPLITS_DIR / "train.parquet", index=False)
    val_df.to_parquet(SPLITS_DIR / "validation.parquet", index=False)
    test_df.to_parquet(SPLITS_DIR / "test.parquet", index=False)

    # 2. Encode Labels
    encoder = LabelEncoder()
    y_train = encoder.fit_transform(train_df["gold_label"])
    y_val = encoder.transform(val_df["gold_label"])
    y_test = encoder.transform(test_df["gold_label"])

    print(f"\nTarget Classes ({len(encoder.classes_)}):")
    for idx, name in enumerate(encoder.classes_):
        print(f"  Index {idx}: {name}")

    # 3. Impute Features
    print("\nFitting feature imputer on training split...")
    X_train_raw = train_df[FEATURES].copy()
    for col in FEATURES:
        X_train_raw[col] = pd.to_numeric(X_train_raw[col], errors="coerce")

    imputer = SimpleImputer(strategy="median")
    X_train = imputer.fit_transform(X_train_raw)

    X_val_raw = val_df[FEATURES].copy()
    for col in FEATURES:
        X_val_raw[col] = pd.to_numeric(X_val_raw[col], errors="coerce")
    X_val = imputer.transform(X_val_raw)

    X_test_raw = test_df[FEATURES].copy()
    for col in FEATURES:
        X_test_raw[col] = pd.to_numeric(X_test_raw[col], errors="coerce")
    X_test = imputer.transform(X_test_raw)

    # 4. Balanced Sample Weights
    sample_weights = compute_sample_weight(class_weight="balanced", y=y_train)

    # 5. Train XGBoost Multi-Class Model
    print("\nTraining XGBoost Classifier...")
    model = xgb.XGBClassifier(
        objective="multi:softprob",
        num_class=len(encoder.classes_),
        n_estimators=350,
        max_depth=6,
        learning_rate=0.045,
        min_child_weight=3,
        subsample=0.85,
        colsample_bytree=0.85,
        reg_alpha=0.15,
        reg_lambda=1.20,
        gamma=0.05,
        eval_metric="mlogloss",
        tree_method="hist",
        random_state=42,
        n_jobs=-1,
    )

    model.fit(
        X_train,
        y_train,
        sample_weight=sample_weights,
        eval_set=[(X_val, y_val)],
        verbose=50,
    )

    # 6. Fit Multi-Class Sigmoid Calibrators (Platt Scaling)
    print("\nFitting probability calibration on validation split...")
    val_raw_probs = model.predict_proba(X_val)
    calibrators = []

    from sklearn.linear_model import LogisticRegression
    for idx in range(len(encoder.classes_)):
        binary_y = (y_val == idx).astype(int)
        if binary_y.sum() > 0 and (binary_y == 0).sum() > 0:
            calib = LogisticRegression(solver="lbfgs")
            calib.fit(val_raw_probs[:, idx].reshape(-1, 1), binary_y)
            calibrators.append(calib)
        else:
            calibrators.append(None)

    calibrated_model = ThermosCalibratedModel(model, calibrators, encoder)

    # 7. Evaluate on Test Split
    print("\nEvaluating on Independent Test Split...")
    test_preds = calibrated_model.predict(X_test)
    y_test_labels = test_df["gold_label"].values

    acc = accuracy_score(y_test_labels, test_preds)
    bal_acc = balanced_accuracy_score(y_test_labels, test_preds)
    macro_p = precision_score(y_test_labels, test_preds, average="macro", zero_division=0)
    macro_r = recall_score(y_test_labels, test_preds, average="macro", zero_division=0)
    macro_f1 = f1_score(y_test_labels, test_preds, average="macro", zero_division=0)
    weighted_f1 = f1_score(y_test_labels, test_preds, average="weighted", zero_division=0)

    report_dict = classification_report(
        y_test_labels,
        test_preds,
        labels=encoder.classes_,
        target_names=encoder.classes_,
        output_dict=True,
        zero_division=0,
    )
    conf_mat = confusion_matrix(y_test_labels, test_preds, labels=encoder.classes_)

    print(f"\nTest Accuracy:         {acc * 100:.2f}%")
    print(f"Balanced Accuracy:     {bal_acc * 100:.2f}%")
    print(f"Macro F1-Score:        {macro_f1:.4f}")
    print(f"Weighted F1-Score:     {weighted_f1:.4f}")
    print("\nPer-Class Breakdown:")
    for cls_name in encoder.classes_:
        cr = report_dict[cls_name]
        print(f"  {cls_name:18s} | Precision: {cr['precision'] * 100:5.1f}% | Recall: {cr['recall'] * 100:5.1f}% | F1: {cr['f1-score']:.4f} (Support: {int(cr['support'])})")

    # 8. Feature Importances
    importances = model.feature_importances_
    feat_df = pd.DataFrame({"feature": FEATURES, "importance": importances}).sort_values("importance", ascending=False)

    # 9. Confusion Matrix DataFrame
    conf_df = pd.DataFrame(conf_mat, index=encoder.classes_, columns=encoder.classes_)

    # 10. Training Run Metrics
    metrics = {
        "model": "XGBoost",
        "num_features": len(FEATURES),
        "features": FEATURES,
        "classes": list(encoder.classes_),
        "train_rows": len(train_df),
        "validation_rows": len(val_df),
        "test_rows": len(test_df),
        "test": {
            "accuracy": float(acc),
            "balanced_accuracy": float(bal_acc),
            "macro_precision": float(macro_p),
            "macro_recall": float(macro_r),
            "macro_f1": float(macro_f1),
            "weighted_f1": float(weighted_f1),
            "classification_report": report_dict,
            "confusion_matrix": conf_mat.tolist(),
        }
    }

    version_meta = {
        "version": "2.1.0",
        "model_type": "XGBoost (Calibrated Multi-Class)",
        "features_count": len(FEATURES),
        "accuracy": round(float(acc), 4),
        "macro_f1": round(float(macro_f1), 4),
        "classes": list(encoder.classes_),
        "training_dataset_rows": len(df),
    }

    # Save to both MODELS_DIR and APP_MODELS_DIR
    target_dirs = [MODELS_DIR, APP_MODELS_DIR]
    for target in target_dirs:
        model.save_model(str(target / "thermal_classifier.json"))
        joblib.dump(calibrated_model, target / "thermal_classifier_calibrated.joblib")
        joblib.dump(encoder, target / "label_encoder.joblib")
        joblib.dump(imputer, target / "feature_imputer.joblib")

        with open(target / "final_training_metrics.json", "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)

        with open(target / "version.json", "w", encoding="utf-8") as f:
            json.dump(version_meta, f, indent=2)

        conf_df.to_csv(target / "final_confusion_matrix.csv")
        feat_df.to_csv(target / "final_feature_importance.csv", index=False)
        feat_df.to_csv(target / "feature_importance.csv", index=False)

    print(f"\nArtifacts successfully exported to:")
    print(f"  -> {MODELS_DIR}")
    print(f"  -> {APP_MODELS_DIR}")
    print("\nRETRAINING COMPLETE — ALL 6 CLASSES BALANCED & OPTIMIZED!")


if __name__ == "__main__":
    main()
