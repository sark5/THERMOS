# THERMOS Thermal Source Classifier

## Model

XGBoost multi-class classifier.

## Intended use

Classify thermal observations into:

- INDUSTRIAL_FLARE
- INDUSTRIAL_FIRE
- MINING
- AGRICULTURAL
- WILDFIRE
- UNCLASSIFIED

## Data

Training data is derived from NASA FIRMS observations and enriched
with spatial, temporal, facility and environmental features.

## Labels

Initial labels are generated through multi-source weak supervision.
A human-reviewed subset is used for independent validation.

## Important limitations

FIRMS is an active-fire/hotspot detection product and does not directly
provide the six THERMOS target classes.

Model performance therefore depends strongly on label quality,
geographic coverage, temporal coverage and contextual feature availability.

## Evaluation

Report only metrics from a genuinely held-out dataset.

Never report training accuracy as final model performance.

## Explainability

SHAP TreeExplainer is used to provide feature-level attribution
for individual model predictions.

## Version

1.0.0