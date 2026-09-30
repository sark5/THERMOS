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
        "acquired_at"
    ] = pd.to_datetime(
        df["acquired_at"],
        utc=True,
        errors="coerce"
    )

    df = df[
        df["acquired_at"].notna()
    ].copy()

    # Historical training period.
    train = df[
        df["acquired_at"].dt.year
        <= 2023
    ].copy()

    # Independent calibration period.
    calibration = df[
        df["acquired_at"].dt.year
        == 2024
    ].copy()

    # Model-selection / validation period.
    validation = df[
        df["acquired_at"].dt.year
        == 2025
    ].copy()

    # Final untouched test period.
    test = df[
        df["acquired_at"].dt.year
        >= 2026
    ].copy()

    splits = {
        "train": train,
        "calibration": calibration,
        "validation": validation,
        "test": test,
    }

    for name, frame in splits.items():

        path = (
            OUTPUT_DIR
            / f"{name}.parquet"
        )

        frame.to_parquet(
            path,
            index=False
        )

        print(
            f"{name:15s}: "
            f"{len(frame)} rows"
        )


if __name__ == "__main__":
    main()