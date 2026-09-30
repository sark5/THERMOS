from pathlib import Path

import pandas as pd


BASE_DIR = Path(
    __file__
).resolve().parent

INPUT = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "firms_labeled.parquet"
)

OUTPUT = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "training_ready.parquet"
)

MIN_LABEL_SCORE = 0.65


def main():

    df = pd.read_parquet(
        INPUT
    )

    selected = df[
        (
            df[
                "label_quality"
            ].isin(
                [
                    "STRONG",
                    "MODERATE"
                ]
            )
        )
        &
        (
            df[
                "label_score"
            ] >= MIN_LABEL_SCORE
        )
        &
        (
            df[
                "thermos_label"
            ] != "UNCLASSIFIED"
        )
    ].copy()

    selected.to_parquet(
        OUTPUT,
        index=False
    )

    print(
        "=" * 60
    )

    print(
        "TRAINING DATA SELECTION"
    )

    print(
        "=" * 60
    )

    print(
        f"Original rows: {len(df)}"
    )

    print(
        f"Selected rows: {len(selected)}"
    )

    print(
        f"Excluded rows: "
        f"{len(df) - len(selected)}"
    )

    print(
        "\nClass distribution:"
    )

    print(
        selected[
            "thermos_label"
        ].value_counts()
    )

    print(
        f"\nSaved: {OUTPUT}"
    )


if __name__ == "__main__":
    main()