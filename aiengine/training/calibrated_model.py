"""
THERMOS Calibrated Model Wrapper
Defines ThermosCalibratedModel class for pickling and inference.
"""

import numpy as np


class ThermosCalibratedModel:

    def __init__(self, base_model, calibrators, encoder):
        self.base_model = base_model
        self.calibrators = calibrators
        self.encoder = encoder
        self.classes_ = encoder.classes_

    def predict_proba(self, X):
        raw_probs = self.base_model.predict_proba(X)
        calibrated_probs = np.zeros_like(raw_probs)
        for idx, calib in enumerate(self.calibrators):
            if calib is not None:
                calibrated_probs[:, idx] = calib.predict_proba(raw_probs[:, idx].reshape(-1, 1))[:, 1]
            else:
                calibrated_probs[:, idx] = raw_probs[:, idx]
        sums = calibrated_probs.sum(axis=1, keepdims=True)
        sums[sums == 0] = 1.0
        return calibrated_probs / sums

    def predict(self, X):
        probs = self.predict_proba(X)
        best_indices = np.argmax(probs, axis=1)
        return self.encoder.inverse_transform(best_indices)
