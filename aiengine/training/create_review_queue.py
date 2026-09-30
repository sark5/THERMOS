from pathlib import Path

import pandas as pd


BASE_DIR = (
    Path(__file__).resolve().parent
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
    / "review_queue.parquet"
)


def main():

    if not INPUT.exists():

        raise FileNotFoundError(
            INPUT
        )

    df = pd.read_parquet(
        INPUT
    )

    required = [
        "event_id",
        "thermos_label",
        "label_score",
    ]

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            "Missing columns: "
            + ", ".join(missing)
        )

    # --------------------------------
    # Keep candidates with useful
    # weak-label evidence.
    # --------------------------------

    candidates = df[
        df["label_score"] >= 0.60
    ].copy()

    # --------------------------------
    # Do NOT only sample the strongest
    # labels.
    #
    # We deliberately include some
    # ambiguous examples.
    # --------------------------------

    samples = []

    for label in sorted(
        candidates[
            "thermos_label"
        ]
        .dropna()
        .unique()
    ):

        label_rows = candidates[
            candidates[
                "thermos_label"
            ] == label
        ]

        n = min(
            150,
            len(label_rows)
        )

        if n > 0:

            samples.append(
                label_rows.sample(
                    n=n,
                    random_state=42
                )
            )

    if not samples:

        raise RuntimeError(
            "No review candidates found."
        )

    review = pd.concat(
        samples,
        ignore_index=True
    )

    review["human_label"] = ""

    review["review_status"] = "PENDING"

    review["reviewer"] = ""

    review["review_notes"] = ""

    review["reviewed_at"] = ""

    review.to_parquet(
        OUTPUT,
        index=False
    )

    print(
        "=" * 60
    )

    print(
        "REVIEW QUEUE CREATED"
    )

    print(
        "=" * 60
    )

    print(
        f"Candidates: {len(review)}"
    )

    print(
        "\nWeak-label distribution:"
    )

    print(
        review[
            "thermos_label"
        ].value_counts()
    )

    print(
        f"\nSaved: {OUTPUT}"
    )


if __name__ == "__main__":
    main()