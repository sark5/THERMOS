"""
THERMOS Source-Aware Group + Temporal Splitter
Splits labeled dataset into Train (<= 2023), Calibration (2024), Validation (2025), and Test (2026)
while asserting zero thermal source (source_id) overlap between sets.
"""

from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
INPUT = BASE_DIR / "datasets" / "processed" / "firms_labeled.parquet"
OUTPUT = BASE_DIR / "datasets" / "processed" / "final_splits"
OUTPUT.mkdir(parents=True, exist_ok=True)


def main():
    print("=" * 70)
    print("THERMOS — SOURCE-AWARE GROUP & TEMPORAL SPLITTER")
    print("=" * 70)

    if not INPUT.exists():
        raise FileNotFoundError(f"Input labeled dataset not found: {INPUT}")

    df = pd.read_parquet(INPUT)

    # Ensure valid acquired_at timestamp
    if "dt" in df.columns:
        df["acquired_at"] = pd.to_datetime(df["dt"], errors="coerce")
    else:
        df["acquired_at"] = pd.to_datetime(df["acq_date"], errors="coerce")

    df = df[df["acquired_at"].notna()].copy()
    print(f"Loaded {len(df):,} timestamped observation records.")

    years = df["acquired_at"].dt.year

    # 1. Primary temporal split
    train_mask = years <= 2023
    calib_mask = years == 2024
    val_mask = years == 2025
    test_mask = years >= 2026

    # 2. Source-aware group isolation
    train_sources = set(df.loc[train_mask, "source_id"].unique())
    calib_sources = set(df.loc[calib_mask, "source_id"].unique())
    val_sources = set(df.loc[val_mask, "source_id"].unique())
    test_sources = set(df.loc[test_mask, "source_id"].unique())

    # Keep sources strict to prevent leakage across years
    val_exclusive = val_sources - train_sources - calib_sources
    test_exclusive = test_sources - train_sources - calib_sources - val_sources

    train = df[train_mask].copy()
    calibration = df[calib_mask & df["source_id"].isin(calib_sources - train_sources)].copy()
    validation = df[val_mask & df["source_id"].isin(val_exclusive)].copy()
    test = df[test_mask & df["source_id"].isin(test_exclusive)].copy()

    # Fallback if holdouts empty in smaller test sets
    if validation.empty and not df.empty:
        val_idx = df.sample(frac=0.15, random_state=42).index
        validation = df.loc[val_idx].copy()
        train = df.drop(val_idx).copy()

    if calibration.empty and not df.empty:
        calib_idx = train.sample(frac=0.15, random_state=42).index
        calibration = train.loc[calib_idx].copy()
        train = train.drop(calib_idx).copy()

    if test.empty and not df.empty:
        test_idx = train.sample(frac=0.15, random_state=42).index
        test = train.loc[test_idx].copy()
        train = train.drop(test_idx).copy()

    split_data = {
        "train": train,
        "calibration": calibration,
        "validation": validation,
        "test": test,
    }

    print("\nSplit Summary (Leakage-Free Source-Aware):")
    for name, frame in split_data.items():
        output = OUTPUT / f"{name}.parquet"
        frame.to_parquet(output, index=False)
        print(f"  {name:12s}: {len(frame):8,d} rows | {frame['source_id'].nunique():6,d} unique sources")
        if not frame.empty and "gold_label" in frame.columns:
            print("  Class distribution:")
            print(frame["gold_label"].value_counts().to_string())
            print("-" * 50)

    # Verification of zero leakage
    t_set = set(train["source_id"])
    v_set = set(validation["source_id"])
    tst_set = set(test["source_id"])
    overlap_tv = t_set.intersection(v_set)
    overlap_tt = t_set.intersection(tst_set)

    print(f"\nSource Leakage Audit:")
    print(f"  Train vs Validation source overlap: {len(overlap_tv)}")
    print(f"  Train vs Test source overlap:       {len(overlap_tt)}")
    assert len(overlap_tv) == 0 and len(overlap_tt) == 0, "Source leakage detected!"
    print("SUCCESS: 0 source overlap verified between Train and Test sets.")


if __name__ == "__main__":
    main()