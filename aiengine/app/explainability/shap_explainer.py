from pathlib import Path

import joblib
import numpy as np
import xgboost as xgb

try:
    import shap
except ModuleNotFoundError:  # pragma: no cover
    shap = None

from app.preprocessing.feature_builder import (
    FEATURE_NAMES,
)


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parents[2]
)

MODEL_DIR = BASE_DIR / "models"
MODEL_CANDIDATES = [
    MODEL_DIR / "thermal_classifier.json",
    MODEL_DIR / "thermal_classifier.joblib",
]
IMPUTER_PATH = MODEL_DIR / "feature_imputer.joblib"


class ThermalSHAPExplainer:

    def __init__(self):

        self.model = None
        self.imputer = None
        self.explainer = None

        if IMPUTER_PATH.exists():
            try:
                self.imputer = joblib.load(IMPUTER_PATH)
            except Exception:
                self.imputer = None

        model_path = next(
            (path for path in MODEL_CANDIDATES if path.exists()),
            None,
        )

        if model_path is not None:
            try:
                self.load()
            except Exception:
                pass

    def load(self):

        model_path = next(
            (path for path in MODEL_CANDIDATES if path.exists()),
            None,
        )

        if model_path is None:
            raise FileNotFoundError(
                "No trained model file was found in the models directory."
            )

        if not IMPUTER_PATH.exists():
            raise FileNotFoundError(
                "Model imputer file was not found."
            )

        self.imputer = joblib.load(IMPUTER_PATH)

        if model_path.suffix.lower() == ".joblib":
            self.model = joblib.load(model_path)
        else:
            self.model = xgb.XGBClassifier()
            self.model.load_model(str(model_path))

        if shap is not None and hasattr(self.model, "predict"):
            try:
                self.explainer = shap.Explainer(self.model, self.imputer.transform)
                return self
            except Exception:
                pass

        self.explainer = None
        return self

    def explain(
        self,
        X,
    ):

        if self.imputer is None:
            self.imputer = joblib.load(IMPUTER_PATH)

        if self.model is None:
            self.load()

        transformed = self.imputer.transform(X)

        if self.explainer is not None:
            shap_values = self.explainer(transformed)
            if hasattr(shap_values, "values"):
                return shap_values.values
            return shap_values

        if hasattr(self.model, "predict"):
            prediction = self.model.predict(transformed)[0]
            feature_abs = np.abs(transformed[0])
            if feature_abs.sum() == 0:
                return np.zeros(transformed.shape[1])
            return feature_abs / feature_abs.sum()

        return np.zeros(transformed.shape[1])
