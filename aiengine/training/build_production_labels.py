from pathlib import Path

import pandas as pd

from label_engine_v2 import (
    classify_row
)


BASE_DIR = (
    Path(__file__).resolve().parent
)

INPUT = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "feature_dataset_v2.parquet"
)

OUTPUT = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "production_labeled.parquet"
)


def main():

    df = pd.read_parquet(
        INPUT
    )

    results = []

    for row in df.to_dict(
        "records"
    ):

        results.append(
            classify_row(
                row
            )
        )

    labels = pd.DataFrame(
        results
    )

    final = pd.concat(
        [
            df.reset_index(
                drop=True
            ),
            labels,
        ],
        axis=1
    )

    final.to_parquet(
        OUTPUT,
        index=False
    )

    print(
        "=" * 70
    )

    print(
        "PRODUCTION LABELING"
    )

    print(
        "=" * 70
    )

    print(
        "\nClass distribution:"
    )

    print(
        final[
            "thermos_label"
        ].value_counts()
    )

    print(
        "\nQuality:"
    )

    print(
        final[
            "label_quality"
        ].value_counts()
    )

    print(
        f"\nSaved: {OUTPUT}"
    )


if __name__ == "__main__":
    main()