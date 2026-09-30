from pathlib import Path

import pandas as pd


BASE_DIR = (
    Path(__file__).resolve().parent
)

DATASET = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "gold_dataset.parquet"
)


CLASSES = [
    "INDUSTRIAL_FLARE",
    "INDUSTRIAL_FIRE",
    "MINING",
    "AGRICULTURAL",
    "WILDFIRE",
    "UNCLASSIFIED",
]


def main():

    df = pd.read_parquet(
        DATASET
    )

    print(
        "=" * 60
    )

    print(
        "GOLD DATASET AUDIT"
    )

    print(
        "=" * 60
    )

    print(
        f"Total rows: {len(df)}"
    )

    print(
        "\nClass distribution:"
    )

    distribution = (
        df["gold_label"]
        .value_counts()
    )

    for label in CLASSES:

        count = int(
            distribution.get(
                label,
                0
            )
        )

        print(
            f"{label:20s} {count}"
        )

    print(
        "\nLabel coverage:"
    )

    print(
        distribution
        .div(len(df))
        .mul(100)
        .round(2)
    )

    print(
        "\nReview status:"
    )

    print(
        df[
            "review_status"
        ].value_counts()
    )


if __name__ == "__main__":
    main()