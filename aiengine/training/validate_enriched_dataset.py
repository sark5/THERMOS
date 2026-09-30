from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent

DATASET = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "firms_enriched.parquet"
)


REQUIRED_FEATURES = [
    "latitude",
    "longitude",
    "frp",
    "confidence_score",
    "persistence_score",
    "anomaly_score",
    "distance_to_facility",
    "industrial_context",
]


def main():

    if not DATASET.exists():

        raise FileNotFoundError(
            DATASET
        )

    df = pd.read_parquet(
        DATASET
    )

    print(
        "=" * 60
    )

    print(
        "ENRICHED DATASET VALIDATION"
    )

    print(
        "=" * 60
    )

    print(
        f"Rows: {len(df)}"
    )

    print(
        f"Columns: {len(df.columns)}"
    )

    missing_features = [
        feature
        for feature in REQUIRED_FEATURES
        if feature not in df.columns
    ]

    if missing_features:

        print(
            "\nMissing features:"
        )

        for feature in missing_features:

            print(
                f"  ❌ {feature}"
            )

    else:

        print(
            "\nRequired features: ✅"
        )

    print(
        "\nMissing percentage:"
    )

    for feature in REQUIRED_FEATURES:

        if feature in df.columns:

            percentage = (
                df[feature].isna().mean()
                * 100
            )

            print(
                f"  {feature}: "
                f"{percentage:.2f}%"
            )

    print(
        "\nFeature statistics:"
    )

    numeric = [
        feature
        for feature in REQUIRED_FEATURES
        if feature in df.columns
    ]

    print(
        df[numeric].describe().T
    )


if __name__ == "__main__":
    main()