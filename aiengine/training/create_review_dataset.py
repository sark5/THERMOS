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
    / "firms_labeled.parquet"
)

OUTPUT = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "review_queue.csv"
)


def main():

    df = pd.read_parquet(
        INPUT
    )

    # Prioritize stronger labels first,
    # but include ambiguous examples.
    strong = df[
        df[
            "label_quality"
        ] == "STRONG"
    ]

    moderate = df[
        df[
            "label_quality"
        ] == "MODERATE"
    ]

    samples = []

    for label in sorted(
        strong["thermos_label"]
        .dropna()
        .unique()
    ):

        subset = strong[
            strong[
                "thermos_label"
            ] == label
        ]

        samples.append(
            subset.sample(
                n=min(
                    100,
                    len(subset)
                ),
                random_state=42
            )
        )

    if moderate.empty is False:

        samples.append(
            moderate.sample(
                n=min(
                    200,
                    len(moderate)
                ),
                random_state=42
            )
        )

    if not samples:

        raise RuntimeError(
            "No records available for review."
        )

    review = pd.concat(
        samples,
        ignore_index=True
    )

    review[
        "human_label"
    ] = ""

    review[
        "review_notes"
    ] = ""

    review[
        "reviewer"
    ] = ""

    review[
        "review_status"
    ] = "PENDING"

    review.to_csv(
        OUTPUT,
        index=False
    )

    print(
        "=" * 60
    )

    print(
        "GOLD DATASET REVIEW QUEUE CREATED"
    )

    print(
        f"Rows: {len(review)}"
    )

    print(
        f"File: {OUTPUT}"
    )


if __name__ == "__main__":
    main()