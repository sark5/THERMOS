from pathlib import Path

import pandas as pd


BASE_DIR = (
    Path(__file__).resolve().parent
)

INPUT = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "review_queue.csv"
)

OUTPUT = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "gold_dataset.parquet"
)

VALID_LABELS = {
    "INDUSTRIAL_FLARE",
    "INDUSTRIAL_FIRE",
    "MINING",
    "AGRICULTURAL",
    "WILDFIRE",
    "UNCLASSIFIED",
}

VALID_STATUSES = {
    "VALIDATED",
    "CORRECTED",
}


def main():

    df = pd.read_csv(
        INPUT
    )

    df[
        "review_status"
    ] = (
        df[
            "review_status"
        ]
        .astype(str)
        .str.upper()
        .str.strip()
    )

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

    gold = df[
        df[
            "review_status"
        ].isin(
            VALID_STATUSES
        )
        &
        df[
            "human_label"
        ].isin(
            VALID_LABELS
        )
    ].copy()

    if gold.empty:

        fallback = pd.read_parquet(
            BASE_DIR
            / "datasets"
            / "processed"
            / "training_ready.parquet"
        )

        if fallback.empty:
            raise RuntimeError(
                "No validated/corrected records available and no "
                "training_ready.parquet fallback was found."
            )

        gold = fallback.copy()
        gold["gold_label"] = (
            gold["thermos_label"].astype(str).str.upper().str.strip()
        )
        gold["label_source"] = "WEAK_LABEL"
        gold["gold_label_confidence"] = gold.get(
            "label_score",
            0.5
        ).fillna(0.5)

        print(
            "WARNING: no validated human-review labels were found; "
            "using the existing weak-label dataset as a fallback."
        )

    else:
        gold[
            "gold_label"
        ] = gold[
            "human_label"
        ]

        gold[
            "label_source"
        ] = "HUMAN_REVIEW"

        gold[
            "gold_label_confidence"
        ] = 1.0

    gold.to_parquet(
        OUTPUT,
        index=False
    )

    print(
        "=" * 60
    )

    print(
        "GOLD DATASET BUILT"
    )

    print(
        "=" * 60
    )

    print(
        f"Gold rows: {len(gold)}"
    )

    print(
        "\nDistribution:"
    )

    print(
        gold[
            "gold_label"
        ].value_counts()
    )

    print(
        f"\nSaved: {OUTPUT}"
    )


if __name__ == "__main__":
    main()