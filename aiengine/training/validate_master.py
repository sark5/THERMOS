from pathlib import Path
import pandas as pd

from dataset_schema import (
    CANONICAL_FIRMS_COLUMNS,
    SP_TRAINING_SOURCES,
)


ROOT = Path(__file__).resolve().parent
DATASET = ROOT / "datasets" / "processed" / "firms_master.parquet"


def fail(message: str):
    raise RuntimeError(f"\nDATASET VALIDATION FAILED:\n{message}")


def main():
    print("=" * 70)
    print("THERMOS — STRICT MASTER DATASET VALIDATION")
    print("=" * 70)

    if not DATASET.exists():
        fail(f"Missing dataset: {DATASET}")

    df = pd.read_parquet(DATASET)

    print(f"\nRows: {len(df):,}")

    missing_columns = [
        c for c in CANONICAL_FIRMS_COLUMNS
        if c not in df.columns
    ]

    if missing_columns:
        fail(
            "Missing required columns:\n"
            + "\n".join(f"  - {c}" for c in missing_columns)
        )

    print("✓ Required columns present")

    # ----------------------------------------------------------
    # Coordinates
    # ----------------------------------------------------------

    if df["latitude"].isna().any():
        fail("Latitude contains null values.")

    if df["longitude"].isna().any():
        fail("Longitude contains null values.")

    if not df["latitude"].between(-90, 90).all():
        fail("Invalid latitude detected.")

    if not df["longitude"].between(-180, 180).all():
        fail("Invalid longitude detected.")

    print("✓ Coordinates valid")

    # ----------------------------------------------------------
    # FRP
    # ----------------------------------------------------------

    if df["frp"].isna().any():
        fail("FRP contains null values.")

    if (df["frp"] < 0).any():
        fail("Negative FRP detected.")

    print("✓ FRP valid")

    # ----------------------------------------------------------
    # Event IDs
    # ----------------------------------------------------------

    duplicate_ids = df["event_id"].duplicated().sum()

    if duplicate_ids:
        fail(
            f"Duplicate event IDs detected: "
            f"{duplicate_ids:,}"
        )

    print("✓ Event IDs unique")

    # ----------------------------------------------------------
    # Sources
    # ----------------------------------------------------------

    invalid_sources = set(df["training_source"].dropna()) - set(
        SP_TRAINING_SOURCES
    )

    if invalid_sources:
        fail(
            "Unexpected training sources found:\n"
            + "\n".join(
                f"  - {x}" for x in sorted(invalid_sources)
            )
        )

    print("✓ Only standard-processing training sources present")

    # ----------------------------------------------------------
    # Date
    # ----------------------------------------------------------

    df["acquired_at"] = pd.to_datetime(
        df["acquired_at"],
        errors="coerce",
        utc=True
    )

    if df["acquired_at"].isna().any():
        fail("Invalid acquired_at timestamp detected.")

    print("✓ Timestamps valid")

    print("\nDataset source distribution:")

    print(
        df["training_source"]
        .value_counts()
        .to_string()
    )

    print("\nDate range:")
    print(f"  START: {df['acquired_at'].min()}")
    print(f"  END:   {df['acquired_at'].max()}")

    print("\n" + "=" * 70)
    print("✓ MASTER DATASET PASSED VALIDATION")
    print("=" * 70)


if __name__ == "__main__":
    main()