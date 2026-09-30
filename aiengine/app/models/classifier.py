from pathlib import Path

import joblib
import xgboost as xgb


class ThermalClassifier:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = (
                Path(__file__).resolve().parents[1]
                / "models"
                / "thermal_classifier.json"
            )
        self.model_path = Path(model_path)
        self.model = None

    def load(self):
        if self.model_path.exists():
            candidate = self.model_path
        else:
            alternate = self.model_path.with_suffix(".joblib")
            candidate = alternate if alternate.exists() else None

        if candidate is None:
            raise FileNotFoundError(
                f"Model not found: {self.model_path}"
            )

        if candidate.suffix.lower() == ".json":
            self.model = xgb.XGBClassifier()
            self.model.load_model(str(candidate))
        else:
            self.model = joblib.load(candidate)

        return self

    def predict(self, features):
        if self.model is None:
            raise RuntimeError(
                "Model has not been loaded."
            )

        predictions = self.model.predict(features)
        probabilities = (
            self.model.predict_proba(features)
            if hasattr(self.model, "predict_proba")
            else None
        )
        return predictions, probabilities
