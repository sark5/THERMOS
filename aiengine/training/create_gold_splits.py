from pathlib import Path

import pandas as pd


BASE_DIR = (
    Path(__file__).resolve().parent
)

INPUT = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "gold_dataset.parquet"
)

OUTPUT = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "splits"
)

OUTPUT.mkdir(
    parents=True,
    exist_ok=True
)


def main():

    dataset = None
    for candidate in [
        INPUT,
        BASE_DIR / "datasets" / "processed" / "training_ready.parquet",
    ]:
        if candidate.exists():
            dataset = pd.read_parquet(candidate)
            break

    if dataset is None:
        raise FileNotFoundError(
            "No labeled dataset found. Expected gold_dataset.parquet "
            "or training_ready.parquet."
        )

    if "gold_label" not in dataset.columns and "thermos_label" in dataset.columns:
        dataset = dataset.copy()
        dataset["gold_label"] = (
            dataset["thermos_label"].astype(str).str.upper().str.strip()
        )

    df = dataset.copy()

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

    train = df[
        df["acquired_at"].dt.year
        <= 2023
    ].copy()

    calibration = df[
        df["acquired_at"].dt.year
        == 2024
    ].copy()

    validation = df[
        df["acquired_at"].dt.year
        == 2025
    ].copy()

    test = df[
        df["acquired_at"].dt.year
        >= 2026
    ].copy()

    split_data = {
        "train": train,
        "calibration": calibration,
        "validation": validation,
        "test": test,
    }

    for name, frame in split_data.items():

        path = (
            OUTPUT
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

        if not frame.empty:

            print(
                frame[
                    "gold_label"
                ].value_counts()
            )

            print()

    print(
        "Gold splits created."
    )


if __name__ == "__main__":
    main()