from pathlib import Path

import pandas as pd

from final_features import (
    CLASSES,
    TARGET,
)


BASE_DIR = (
    Path(__file__).resolve().parent
)

INPUT = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "final_training_matrix.parquet"
)


MINIMUM = 50


def main():

    df = pd.read_parquet(
        INPUT
    )

    counts = (
        df[TARGET]
        .value_counts()
    )

    failed = []

    print(
        "=" * 70
    )

    print(
        "TRAINING COVERAGE"
    )

    print(
        "=" * 70
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
            if count >= MINIMUM
            else "FAIL"
        )

        print(
            f"{label:22s}"
            f"{count:8d}"
            f"   {status}"
        )

        if count < MINIMUM:

            failed.append(
                label
            )

    if failed:

        print()
        print(
            "Insufficient samples:"
        )

        for label in failed:

            print(
                f"  - {label}"
            )

        raise RuntimeError(
            "Training should not proceed "
            "until class coverage is improved."
        )

    print()
    print(
        "All classes meet the minimum."
    )


if __name__ == "__main__":
    main()