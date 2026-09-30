from pathlib import Path

import pandas as pd

from final_features import (
    FEATURES,
    TARGET,
    CLASSES,
)


BASE_DIR = (
    Path(__file__).resolve().parent
)

INPUT_CANDIDATES = [
    BASE_DIR / "datasets" / "processed" / "production_labeled.parquet",
    BASE_DIR / "datasets" / "processed" / "gold_dataset.parquet",
    BASE_DIR / "datasets" / "processed" / "final_training_dataset.parquet",
    BASE_DIR / "datasets" / "processed" / "training_ready.parquet",
]

OUTPUT = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "final_training_matrix.parquet"
)


def main():

    selected_input = next(
        (path for path in INPUT_CANDIDATES if path.exists()),
        None,
    )

    if selected_input is None:
        raise FileNotFoundError(
            "No supported labeled dataset found. Expected one of:\n"
            + "\n".join(str(path) for path in INPUT_CANDIDATES)
        )

    df = pd.read_parquet(
        selected_input
    )

    print(
        f"Using dataset: {selected_input.name}"
    )
    print(
        f"Raw labeled rows: {len(df)}"
    )

    target_column = (
        TARGET
        if TARGET in df.columns
        else "thermos_label"
    )

    if target_column not in df.columns:
        raise ValueError(
            f"Missing target column. Expected '{TARGET}' or 'thermos_label'."
        )

    df[target_column] = (
        df[target_column]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    if TARGET in df.columns:
        df[TARGET] = df[TARGET].astype(str).str.upper().str.strip()

    valid_classes = [
        value for value in CLASSES if value in df[target_column].unique()
    ]

    if not valid_classes:
        raise ValueError(
            f"No valid class values found in '{target_column}'."
        )

    df = df[
        df[target_column].isin(
            CLASSES
        )
    ].copy()

    available_features = [
        column for column in FEATURES if column in df.columns
    ]

    if not available_features:
        raise ValueError(
            "No matching feature columns found in the current dataset."
        )

    for column in available_features:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    for column in FEATURES:
        if column not in df.columns:
            df[column] = 0.0

    required = [
        "event_id",
        "acquired_at",
        "latitude",
        "longitude",
        "frp",
        target_column,
    ]

    df = df.dropna(
        subset=[column for column in required if column in df.columns]
    )

    df["acquired_at"] = pd.to_datetime(
        df["acquired_at"],
        utc=True,
        errors="coerce"
    )

    df = df[
        df["acquired_at"].notna()
    ]

    df = df.drop_duplicates(
        subset=[
            "event_id"
        ]
    )

    keep = [
        "event_id",
        "source_id",
        "latitude",
        "longitude",
        "acquired_at",
        target_column,
    ] + FEATURES

    keep = [
        column for column in keep if column in df.columns
    ]

    matrix = df[
        keep
    ].copy()

    matrix = matrix.sort_values(
        "acquired_at"
    ).reset_index(
        drop=True
    )

    matrix.to_parquet(
        OUTPUT,
        index=False
    )

    print()
    print(
        "=" * 70
    )

    print(
        "FINAL REAL TRAINING MATRIX"
    )

    print(
        "=" * 70
    )

    print(
        f"Rows: {len(matrix)}"
    )

    print(
        f"Features: {len(FEATURES)}"
    )

    class_column = (
        TARGET
        if TARGET in matrix.columns
        else target_column
    )

    print(
        "\nClass distribution:"
    )

    print(
        matrix[
            class_column
        ].value_counts()
    )

    print(
        f"\nSaved:\n{OUTPUT}"
    )


if __name__ == "__main__":
    main()