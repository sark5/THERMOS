from pathlib import Path

import pandas as pd


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
)

INPUT = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "gold_dataset.parquet"
)

OUTPUT_DIR = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "splits"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def main():

    df = pd.read_parquet(
        INPUT
    )

    df[
        "event_time"
    ] = pd.to_datetime(
        df[
            "acquired_at"
        ],
        utc=True,
        errors="coerce"
    )

    train = df[
        df[
            "event_time"
        ].dt.year <= 2024
    ]

    validation = df[
        df[
            "event_time"
        ].dt.year == 2025
    ]

    test = df[
        df[
            "event_time"
        ].dt.year >= 2026
    ]

    train.to_parquet(
        OUTPUT_DIR
        / "train.parquet",
        index=False
    )

    validation.to_parquet(
        OUTPUT_DIR
        / "validation.parquet",
        index=False
    )

    test.to_parquet(
        OUTPUT_DIR
        / "test.parquet",
        index=False
    )

    print(
        "=" * 60
    )

    print(
        "TEMPORAL DATASET SPLIT"
    )

    print(
        "=" * 60
    )

    print(
        f"Train: {len(train)}"
    )

    print(
        f"Validation: {len(validation)}"
    )

    print(
        f"Test: {len(test)}"
    )


if __name__ == "__main__":
    main()