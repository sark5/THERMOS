from pathlib import Path

import pandas as pd


BASE_DIR = (
    Path(__file__).resolve().parent
)

GOLD_INPUT = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "gold_dataset.parquet"
)

WEAK_LABEL_INPUT = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "training_ready.parquet"
)

OUTPUT = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "final_training_dataset.parquet"
)


VALID_LABELS = {
    "INDUSTRIAL_FLARE",
    "INDUSTRIAL_FIRE",
    "MINING",
    "AGRICULTURAL",
    "WILDFIRE",
    "UNCLASSIFIED",
}


def main():

    if GOLD_INPUT.exists():

        input_path = GOLD_INPUT
        label_column = "human_label"

    elif WEAK_LABEL_INPUT.exists():

        input_path = WEAK_LABEL_INPUT
        label_column = "thermos_label"

        print(
            "Gold dataset not found; using weak labels from "
            "training_ready.parquet."
        )

    else:

        raise FileNotFoundError(
            "No training input found. Expected either: "
            f"{GOLD_INPUT} or {WEAK_LABEL_INPUT}"
        )

    df = pd.read_parquet(
        input_path
    )

    print(
        f"Input rows: {len(df)}"
    )

    if label_column not in df.columns:

        raise ValueError(
            f"{label_column} column is missing."
        )

    if label_column != "human_label":

        df["human_label"] = df[label_column]

    df[
        "human_label"
    ] = (
        df[
            "human_label"
        ]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    df = df[
        df[
            "human_label"
        ].isin(
            VALID_LABELS
        )
    ].copy()

    # Remove records that do not have
    # enough fundamental FIRMS information.
    required = [
        "event_id",
        "acquired_at",
        "latitude",
        "longitude",
        "frp",
    ]

    for column in required:

        if column not in df.columns:

            raise ValueError(
                f"Missing required column: {column}"
            )

    df = df[
        df["latitude"].notna()
        & df["longitude"].notna()
        & df["frp"].notna()
    ]

    # Normalize timestamps.
    df[
        "acquired_at"
    ] = pd.to_datetime(
        df["acquired_at"],
        utc=True,
        errors="coerce"
    )

    df = df[
        df["acquired_at"].notna()
    ]

    # Remove exact event duplicates.
    df = df.drop_duplicates(
        subset=[
            "event_id"
        ]
    )

    # Sort chronologically.
    df = df.sort_values(
        "acquired_at"
    ).reset_index(
        drop=True
    )

    df.to_parquet(
        OUTPUT,
        index=False
    )

    print()
    print(
        "=" * 60
    )

    print(
        "FINAL TRAINING DATA PREPARED"
    )

    print(
        "=" * 60
    )

    print(
        f"Rows: {len(df)}"
    )

    print(
        "\nClass distribution:"
    )

    print(
        df[
            "human_label"
        ].value_counts()
    )

    print(
        f"\nSaved: {OUTPUT}"
    )


if __name__ == "__main__":
    main()