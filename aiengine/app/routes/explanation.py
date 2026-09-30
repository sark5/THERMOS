from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import numpy as np
import pandas as pd

from app.explainability.shap_explainer import (
    ThermalSHAPExplainer,
)

from app.explainability.explanation_builder import (
    build_explanation,
)

from app.preprocessing.feature_builder import (
    FEATURE_NAMES,
)


router = APIRouter()

explainer = ThermalSHAPExplainer()


def ensure_explainer_loaded():
    if explainer.imputer is None or explainer.explainer is None or explainer.model is None:
        explainer.load()


class ExplanationRequest(BaseModel):

    frp: float = 0

    bright_ti4: float = 0

    bright_ti5: float = 0

    confidence_score: float = 0

    persistence_score: float = 0

    anomaly_score: float = 0

    distance_to_facility: float = 99999

    industrial_context: float = 0

    forest_context: float = 0

    agricultural_context: float = 0

    builtup_context: float = 0

    ndvi_mean: float = 0

    ndvi_std: float = 0

    ndmi_mean: float = 0

    ndmi_std: float = 0

    sentinel2_quality_score: float = 0

    day_night_numeric: float = 0

    firms_type: float = 0


@router.post("/")
def explain(
    request: ExplanationRequest
):

    try:

        ensure_explainer_loaded()

        values = request.model_dump()

        frame = pd.DataFrame(
            [
                {
                    feature:
                        values.get(
                            feature,
                            0
                        )
                    for feature in FEATURE_NAMES
                }
            ]
        )

        transformed = (
            explainer.imputer.transform(
                frame
            )
        )

        if explainer.explainer is not None:
            shap_values = (
                explainer.explainer.shap_values(
                    transformed
                )
            )

            # Multi-class XGBoost/SHAP output
            # can be class-indexed.
            if isinstance(
                shap_values,
                list
            ):

                prediction = (
                    explainer.model.predict(
                        transformed
                    )[0]
                )

                selected_values = (
                    shap_values[
                        int(prediction)
                    ][0]
                )

            else:

                array = shap_values

                if array.ndim == 3:

                    prediction = (
                        explainer.model.predict(
                            transformed
                        )[0]
                    )

                    selected_values = (
                        array[
                            0,
                            :,
                            int(prediction)
                        ]
                    )

                else:

                    selected_values = (
                        array[0]
                    )

        else:
            raw_values = transformed[0]
            feature_abs = np.abs(raw_values)
            if feature_abs.sum() == 0:
                selected_values = np.zeros_like(raw_values)
            else:
                selected_values = feature_abs / feature_abs.sum()

        explanation = (
            build_explanation(
                feature_values=[
                    values.get(
                        feature,
                        0
                    )
                    for feature in FEATURE_NAMES
                ],
                shap_values=selected_values,
                top_n=6,
            )
        )

        return {
            "explanation": explanation
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )
