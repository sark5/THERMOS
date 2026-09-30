import pandas as pd


def build_error_table(
    dataframe,
    y_true,
    y_pred,
    probabilities,
    label_encoder,
):

    result = dataframe.copy()

    true_labels = (
        label_encoder.inverse_transform(
            y_true
        )
    )

    predicted_labels = (
        label_encoder.inverse_transform(
            y_pred
        )
    )

    result[
        "true_label"
    ] = true_labels

    result[
        "predicted_label"
    ] = predicted_labels

    result[
        "prediction_confidence"
    ] = probabilities.max(
        axis=1
    )

    result[
        "correct"
    ] = (
        result["true_label"]
        == result["predicted_label"]
    )

    return result


def save_errors(
    error_table,
    output_path
):

    errors = error_table[
        ~error_table["correct"]
    ].copy()

    errors = errors.sort_values(
        "prediction_confidence",
        ascending=False
    )

    errors.to_parquet(
        output_path,
        index=False
    )

    return errors