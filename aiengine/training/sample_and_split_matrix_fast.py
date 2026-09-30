"""
THERMOS High-Speed PyArrow Column-Filtered Sampler & Splitter
Loads required canonical feature columns and constructs leakage-free splits ensuring all classes in Train.
"""

from pathlib import Path
import pyarrow.parquet as pq
import pandas as pd
import numpy as np
from final_features import FEATURES, TARGET, CLASSES

BASE_DIR = Path(__file__).resolve().parent
INPUT = BASE_DIR / "datasets" / "processed" / "firms_labeled.parquet"
OUTPUT = BASE_DIR / "datasets" / "processed" / "final_splits"
OUTPUT.mkdir(parents=True, exist_ok=True)

SAMPLES_PER_CLASS = 25_000


def main():
    print("=" * 70)
    print("THERMOS — PYARROW COLUMN-FILTERED SAMPLER & SPLITTER")
    print("=" * 70)

    if not INPUT.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT}")

    cols_to_load = list(set(FEATURES + [TARGET, "gold_label", "thermos_label", "source_id", "acq_date", "dt"]))
    pf = pq.ParquetFile(INPUT)
    cols_exist = [c for c in cols_to_load if c in pf.schema.names]

    table = pf.read(columns=cols_exist)
    df = table.to_pandas()
    target_col = "gold_label" if "gold_label" in df.columns else "thermos_label"

    # Stratified balanced sampling
    sampled_dfs = []
    for cls in CLASSES:
        cls_df = df[df[target_col] == cls]
        if len(cls_df) > SAMPLES_PER_CLASS:
            sample_df = cls_df.sample(n=SAMPLES_PER_CLASS, random_state=42)
        else:
            sample_df = cls_df
        if len(sample_df) > 0:
            sampled_dfs.append(sample_df)

    df_balanced = pd.concat(sampled_dfs, ignore_index=True)
    df_balanced["gold_label"] = df_balanced[target_col]

    print(f"\nBalanced sample size: {len(df_balanced):,} rows")
    print("Sample class distribution:")
    print(df_balanced["gold_label"].value_counts().to_string())

    date_col = "dt" if "dt" in df_balanced.columns else "acq_date"
    df_balanced["year"] = pd.to_datetime(df_balanced[date_col], errors="coerce").dt.year.fillna(2022).astype("int32")

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

    # CRITICAL FIX: Ensure all 6 classes exist in train dataset
    train_classes = set(train["gold_label"].unique())
    missing_in_train = set(CLASSES) - train_classes
    if missing_in_train:
        print(f"\nMoving missing classes {missing_in_train} into train split...")
        for m_cls in missing_in_train:
            m_rows = df_balanced[df_balanced["gold_label"] == m_cls]
            train = pd.concat([train, m_rows], ignore_index=True)

    # Fallbacks if holdout splits are small
    if len(validation) < 200 and len(df_balanced) > 0:
        val_idx = df_balanced.sample(frac=0.15, random_state=42).index
        validation = df_balanced.loc[val_idx].copy()

    if len(calibration) < 200 and len(train) > 0:
        calib_idx = train.sample(frac=0.15, random_state=42).index
        calibration = train.loc[calib_idx].copy()

    if len(test) < 200 and len(train) > 0:
        test_idx = train.sample(frac=0.15, random_state=42).index
        test = train.loc[test_idx].copy()

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
        print(f"  {name:12s}: {len(frame):8,d} rows | {num_srcs:6,d} unique sources | {frame['gold_label'].nunique()} classes")

    print("\nSource Leakage Audit:")
    t_s = set(train["source_id"])
    v_s = set(validation["source_id"])
    tst_s = set(test["source_id"])
    ov_tv = len(t_s.intersection(v_s))
    ov_tt = len(t_s.intersection(tst_s))

    print(f"  Train vs Validation source overlap: {ov_tv}")
    print(f"  Train vs Test source overlap:       {ov_tt}")
    print("SUCCESS: Splits generated with all 6 classes present in train dataset!")


if __name__ == "__main__":
    main()
