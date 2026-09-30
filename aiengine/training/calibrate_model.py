"""
THERMOS Probability Calibration Engine
Fits per-class Sigmoid Calibrators (LogisticRegression) on pre-fit XGBoost probability outputs
using the calibration holdout dataset.
"""

from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from model_features import FEATURE_COLUMNS, LABELS
from calibrated_model import ThermosCalibratedModel

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "datasets" / "processed" / "final_splits"
MODEL_DIR = BASE_DIR / "models"
BASE_MODEL_PATH = MODEL_DIR / "thermos_xgboost_final.json"
ENCODER_PATH = MODEL_DIR / "label_encoder.joblib"
IMPUTER_PATH = MODEL_DIR / "feature_imputer.joblib"
OUTPUT_MODEL = MODEL_DIR / "thermal_classifier_calibrated.joblib"
OUTPUT_META = MODEL_DIR / "calibration_metadata.json"


def main():
    print("=" * 70)
    print("THERMOS — PROBABILITY CALIBRATION")
    print("=" * 70)

    calib_path = DATA_DIR / "calibration.parquet"
    if not calib_path.exists():
        calib_path = BASE_DIR / "datasets" / "processed" / "splits" / "calibration.parquet"

    if not calib_path.exists():
        raise FileNotFoundError(f"Calibration split not found at: {calib_path}")

    model = xgb.XGBClassifier()
    model.load_model(BASE_MODEL_PATH)
    encoder = joblib.load(ENCODER_PATH)
    imputer = joblib.load(IMPUTER_PATH)

    calibration = pd.read_parquet(calib_path)
    label_col = "gold_label" if "gold_label" in calibration.columns else "human_label"
    calibration = calibration[calibration[label_col].isin(encoder.classes_)].copy()

    X = calibration[FEATURE_COLUMNS].copy()
    for col in FEATURE_COLUMNS:
        X[col] = pd.to_numeric(X[col], errors="coerce")
    X_mat = imputer.transform(X)

    y = encoder.transform(calibration[label_col])
    raw_probs = model.predict_proba(X_mat)

    calibrators = []
    num_classes = len(encoder.classes_)

    for k in range(num_classes):
        y_binary = (y == k).astype(int)
        if y_binary.sum() > 0 and (y_binary == 0).sum() > 0:
            lr = LogisticRegression(solver="lbfgs")
            lr.fit(raw_probs[:, k].reshape(-1, 1), y_binary)
            calibrators.append(lr)
        else:
            calibrators.append(None)

    calibrated_wrapper = ThermosCalibratedModel(model, calibrators, encoder)

    joblib.dump(calibrated_wrapper, OUTPUT_MODEL)

    metadata = {
        "method": "sigmoid_logistic",
        "rows": len(calibration),
        "base_model": str(BASE_MODEL_PATH),
        "classes": list(encoder.classes_),
    }

    with open(OUTPUT_META, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print("PROBABILITY CALIBRATION COMPLETE")
    print(f"Calibrated model dumped to: {OUTPUT_MODEL}")
    print(f"Metadata dumped to: {OUTPUT_META}")


if __name__ == "__main__":
    main()