from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parent
DATASET = ROOT / "datasets" / "processed" / "firms_master.parquet"


def main():
    if not DATASET.exists():
        raise FileNotFoundError(
            f"Dataset not found:\n{DATASET}\n"
            "Run build_master_firms.py first."
        )

    df = pd.read_parquet(DATASET)

    print("=" * 70)
    print("THERMOS — MASTER FIRMS DATASET AUDIT")
    print("=" * 70)

    print(f"\nRows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumns:")
    for col in df.columns:
        print(f"  - {col}")

    print("\nDate range:")
    if "acquired_at" in df.columns:
        print(f"  {df['acquired_at'].min()}")
        print(f"  {df['acquired_at'].max()}")

    if "training_source" in df.columns:
        print("\nTraining sources:")
        print(df["training_source"].value_counts(dropna=False))

    if "source_year" in df.columns:
        print("\nRows by year:")
        print(
            df["source_year"]
            .value_counts()
            .sort_index()
            .to_string()
        )

    print("\nMissing-value percentage:")
    missing = (
        df.isna()
        .mean()
        .mul(100)
        .sort_values(ascending=False)
    )

    for col, pct in missing.items():
        print(f"  {col:30s} {pct:8.2f}%")

    print("\nLatitude range:")
    print(f"  {df['latitude'].min()} → {df['latitude'].max()}")

    print("\nLongitude range:")
    print(f"  {df['longitude'].min()} → {df['longitude'].max()}")

    print("\nFRP statistics:")
    print(df["frp"].describe())

    if "confidence_score" in df.columns:
        print("\nConfidence statistics:")
        print(df["confidence_score"].describe())

    if "firms_type" in df.columns:
        print("\nFIRMS type distribution:")
        print(df["firms_type"].value_counts(dropna=False).sort_index())

    print("\nDuplicate event IDs:")
    if "event_id" in df.columns:
        dup_count = df["event_id"].duplicated().sum()
        print(f"  {dup_count:,}")

    print("\n" + "=" * 70)
    print("AUDIT COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()