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
    / "review_queue.csv"
)

OUTPUT = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "gold_dataset.parquet"
)


VALID_STATUSES = {
    "VALIDATED",
    "CORRECTED",
}


VALID_LABELS = {
    "INDUSTRIAL_FLARE",
    "INDUSTRIAL_FIRE",
    "MINING",
    "AGRICULTURAL",
    "WILDFIRE",
    "UNCLASSIFIED",
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
                "No validated review records are available and no "
                "training_ready.parquet fallback exists."
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
            "WARNING: review queue has no accepted labels; using the "
            "existing weak-label dataset as the gold fallback."
        )

    else:
        gold["gold_label"] = gold["human_label"]
        gold["label_source"] = "HUMAN_REVIEW"
        gold["gold_label_confidence"] = 1.0

    gold.to_parquet(
        OUTPUT,
        index=False
    )

    print(
        "=" * 60
    )

    print(
        "GOLD DATASET CREATED"
    )

    print(
        f"Reviewed rows: {len(df)}"
    )

    print(
        f"Gold rows: {len(gold)}"
    )

    print(
        "\nClass distribution:"
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