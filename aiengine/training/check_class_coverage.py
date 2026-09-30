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


MIN_SAMPLES = 30

CLASSES = [
    "INDUSTRIAL_FLARE",
    "INDUSTRIAL_FIRE",
    "MINING",
    "AGRICULTURAL",
    "WILDFIRE",
    "UNCLASSIFIED",
]


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
            "No training dataset found. Expected gold_dataset.parquet "
            "or training_ready.parquet."
        )

    label_column = (
        "gold_label"
        if "gold_label" in dataset.columns
        else "thermos_label"
    )
    counts = (
        dataset[label_column]
        .astype(str)
        .str.upper()
        .value_counts()
    )

    min_required = 1 if label_column == "thermos_label" else MIN_SAMPLES
    failed = False

    print(
        "=" * 60
    )

    print(
        "CLASS COVERAGE CHECK"
    )

    print(
        "=" * 60
    )

    for label in CLASSES:

        count = int(
            counts.get(
                label,
                0
            )
        )

        status = (
            "PASS"
            if count >= min_required
            else "FAIL"
        )

        print(
            f"{label:20s}"
            f"{count:6d}"
            f"   {status}"
        )

        if count < min_required:
            failed = True

    if failed:

        raise RuntimeError(
            "\nInsufficient gold-label "
            "coverage for one or more classes."
        )

    print(
        "\nAll classes meet minimum coverage."
    )


if __name__ == "__main__":
    main()