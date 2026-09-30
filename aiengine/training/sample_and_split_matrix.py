"""
THERMOS Balanced Sampling & Leakage-Free Source-Aware Splitter
Creates high-performance balanced splits across all 6 classes from the labeled matrix.
"""

from pathlib import Path
import pyarrow.parquet as pq
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent
INPUT = BASE_DIR / "datasets" / "processed" / "firms_labeled.parquet"
OUTPUT = BASE_DIR / "datasets" / "processed" / "final_splits"
OUTPUT.mkdir(parents=True, exist_ok=True)

SAMPLES_PER_CLASS = 40_000


def main():
    print("=" * 70)
    print("THERMOS — BALANCED SAMPLING & LEAKAGE-FREE SPLITTER")
    print("=" * 70)

    if not INPUT.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT}")

    print(f"Reading dataset via PyArrow: {INPUT}...")
    full_df = pd.read_parquet(INPUT)
    print(f"Total labeled records: {len(full_df):,}")

    # Stratified balanced sampling per class
    sampled_dfs = []
    for cls in full_df["gold_label"].unique():
        cls_df = full_df[full_df["gold_label"] == cls]
        if len(cls_df) > SAMPLES_PER_CLASS:
            sample_df = cls_df.sample(n=SAMPLES_PER_CLASS, random_state=42)
        else:
            sample_df = cls_df
        sampled_dfs.append(sample_df)

    df_balanced = pd.concat(sampled_dfs, ignore_index=True)
    print(f"\nBalanced sample dataset size: {len(df_balanced):,} rows")
    print("Sample class distribution:")
    print(df_balanced["gold_label"].value_counts().to_string())

    # Ensure timestamp parsing
    date_col = "dt" if "dt" in df_balanced.columns else "acq_date"
    df_balanced["year"] = pd.to_datetime(df_balanced[date_col], errors="coerce").dt.year.fillna(2022).astype("int32")

    # Split: Train (<=2023), Calibration (2024), Validation (2025), Test (2026)
    years = df_balanced["year"]
    train_mask = years <= 2023
    calib_mask = years == 2024
    val_mask = years == 2025
    test_mask = years >= 2026

    train_sources = set(df_balanced.loc[train_mask, "source_id"].unique())
    calib_sources = set(df_balanced.loc[calib_mask, "source_id"].unique()) - train_sources
    val_sources = set(df_balanced.loc[val_mask, "source_id"].unique()) - train_sources - calib_sources
    test_sources = set(df_balanced.loc[test_mask, "source_id"].unique()) - train_sources - calib_sources - val_sources

    train = df_balanced[train_mask].copy()
    calibration = df_balanced[calib_mask & df_balanced["source_id"].isin(calib_sources)].copy()
    validation = df_balanced[val_mask & df_balanced["source_id"].isin(val_sources)].copy()
    test = df_balanced[test_mask & df_balanced["source_id"].isin(test_sources)].copy()

    # Fallbacks if holdout sets are small due to temporal distribution in sample
    if len(validation) < 500 and len(df_balanced) > 0:
        val_idx = df_balanced.sample(frac=0.15, random_state=42).index
        validation = df_balanced.loc[val_idx].copy()
        train = df_balanced.drop(val_idx).copy()

    if len(calibration) < 500 and len(train) > 0:
        calib_idx = train.sample(frac=0.15, random_state=42).index
        calibration = train.loc[calib_idx].copy()
        train = train.drop(calib_idx).copy()

    if len(test) < 500 and len(train) > 0:
        test_idx = train.sample(frac=0.15, random_state=42).index
        test = train.loc[test_idx].copy()
        train = train.drop(test_idx).copy()

    split_map = {
        "train": train,
        "calibration": calibration,
        "validation": validation,
        "test": test,
    }

    print("\nSaving final splits to:", OUTPUT)
    for name, frame in split_map.items():
        out_path = OUTPUT / f"{name}.parquet"
        frame.to_parquet(out_path, index=False)
        num_srcs = frame["source_id"].nunique() if "source_id" in frame.columns else 0
        print(f"  {name:12s}: {len(frame):8,d} rows | {num_srcs:6,d} unique sources")

    # Leakage check
    t_s = set(train["source_id"])
    v_s = set(validation["source_id"])
    tst_s = set(test["source_id"])
    ov_tv = len(t_s.intersection(v_s))
    ov_tt = len(t_s.intersection(tst_s))

    print(f"\nSource Leakage Audit:")
    print(f"  Train vs Validation source overlap: {ov_tv}")
    print(f"  Train vs Test source overlap:       {ov_tt}")
    assert ov_tv == 0 and ov_tt == 0, "Source leakage detected!"
    print("SUCCESS: 0 source overlap verified between Train, Validation, and Test sets!")


if __name__ == "__main__":
    main()
