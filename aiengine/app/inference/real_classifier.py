from pathlib import Path

import joblib
import numpy as np
import xgboost as xgb

from app.preprocessing.feature_builder import (
    build_feature_vector,
)

from app.models.classes import (
    THERMAL_CLASSES,
)


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parents[2]
)

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "thermal_classifier.json"
)

ENCODER_PATH = (
    BASE_DIR
    / "models"
    / "label_encoder.joblib"
)

IMPUTER_PATH = (
    BASE_DIR
    / "models"
    / "feature_imputer.joblib"
)


class RealThermalClassifier:

    def __init__(self):

        self.model = None
        self.encoder = None
        self.imputer = None

    def load(self):

        if not MODEL_PATH.exists():

            raise FileNotFoundError(
                MODEL_PATH
            )

        if not ENCODER_PATH.exists():

            raise FileNotFoundError(
                ENCODER_PATH
            )

        if not IMPUTER_PATH.exists():

            raise FileNotFoundError(
                IMPUTER_PATH
            )

        self.model = (
            xgb.XGBClassifier()
        )

        self.model.load_model(
            MODEL_PATH
        )

        self.encoder = joblib.load(
            ENCODER_PATH
        )

        self.imputer = joblib.load(
            IMPUTER_PATH
        )

        return self

    def predict(
        self,
        event
    ):

        if self.model is None:

            self.load()

        vector = np.asarray(
            [
                build_feature_vector(
                    event
                )
            ],
            dtype=float
        )

        vector = self.imputer.transform(
            vector
        )

        probabilities = (
            self.model.predict_proba(
                vector
            )[0]
        )

        class_index = int(
            np.argmax(
                probabilities
            )
        )

        label = (
            self.encoder.inverse_transform(
                [class_index]
            )[0]
        )

        confidence = float(
            probabilities[
                class_index
            ]
        )

        probability_map = {}

        for index, probability in (
            enumerate(
                probabilities
            )
        ):

            class_name = (
                self.encoder.inverse_transform(
                    [index]
                )[0]
            )

            probability_map[
                class_name
            ] = round(
                float(probability),
                4
            )

        return {
            "classification": label,

            "confidence": round(
                confidence,
                4
            ),

            "probabilities":
                probability_map,

            "model":
                "THERMOS-XGBoost-REAL-FIRMS",
        }
