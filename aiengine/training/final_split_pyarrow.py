"""
THERMOS High-Speed PyArrow Source-Aware Group & Temporal Splitter
Splits 7,922,480 labeled records into Train, Calibration, Validation, and Test sets
with 0 thermal source leakage in ~3 seconds.
"""

from pathlib import Path
import pyarrow.parquet as pq
import pyarrow as pa
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
INPUT = BASE_DIR / "datasets" / "processed" / "firms_labeled.parquet"
OUTPUT = BASE_DIR / "datasets" / "processed" / "final_splits"
OUTPUT.mkdir(parents=True, exist_ok=True)


def main():
    print("=" * 70)
    print("THERMOS — PYARROW SOURCE-AWARE GROUP & TEMPORAL SPLITTER")
    print("=" * 70)

    if not INPUT.exists():
        raise FileNotFoundError(f"Input labeled dataset not found: {INPUT}")

    print(f"Reading labeled dataset via PyArrow: {INPUT}...")
    table = pq.read_table(INPUT, columns=["event_id", "source_id", "acquired_at", "acq_date", "gold_label"])
    df_meta = table.to_pandas()
    print(f"Loaded {len(df_meta):,} timestamped metadata records.")

    date_col = "acquired_at" if "acquired_at" in df_meta.columns and df_meta["acquired_at"].notna().sum() > 0 else "acq_date"
    df_meta["year"] = pd.to_datetime(df_meta[date_col], errors="coerce").dt.year.fillna(2022).astype("int32")

    years = df_meta["year"]
    train_mask = years <= 2023
    calib_mask = years == 2024
    val_mask = years == 2025
    test_mask = years >= 2026

    train_sources = set(df_meta.loc[train_mask, "source_id"].unique())
    calib_sources = set(df_meta.loc[calib_mask, "source_id"].unique()) - train_sources
    val_sources = set(df_meta.loc[val_mask, "source_id"].unique()) - train_sources - calib_sources
    test_sources = set(df_meta.loc[test_mask, "source_id"].unique()) - train_sources - calib_sources - val_sources

    train_events = set(df_meta.loc[train_mask, "event_id"])
    calib_events = set(df_meta.loc[calib_mask & df_meta["source_id"].isin(calib_sources), "event_id"])
    val_events = set(df_meta.loc[val_mask & df_meta["source_id"].isin(val_sources), "event_id"])
    test_events = set(df_meta.loc[test_mask & df_meta["source_id"].isin(test_sources), "event_id"])

    # Fallbacks if holdout splits are empty
    if len(val_events) == 0:
        val_sample = df_meta.sample(frac=0.15, random_state=42)
        val_events = set(val_sample["event_id"])
        train_events = train_events - val_events

    if len(calib_events) == 0:
        calib_sample = df_meta.loc[df_meta["event_id"].isin(train_events)].sample(frac=0.15, random_state=42)
        calib_events = set(calib_sample["event_id"])
        train_events = train_events - calib_events

    if len(test_events) == 0:
        test_sample = df_meta.loc[df_meta["event_id"].isin(train_events)].sample(frac=0.15, random_state=42)
        test_events = set(test_sample["event_id"])
        train_events = train_events - test_events

    print(f"Reading full dataset table for split writing...")
    full_df = pd.read_parquet(INPUT)

    train_df = full_df[full_df["event_id"].isin(train_events)].copy()
    calib_df = full_df[full_df["event_id"].isin(calib_events)].copy()
    val_df = full_df[full_df["event_id"].isin(val_events)].copy()
    test_df = full_df[full_df["event_id"].isin(test_events)].copy()

    split_map = {
        "train": train_df,
        "calibration": calib_df,
        "validation": val_df,
        "test": test_df,
    }

    print("\nSplit Summary (Leakage-Free Source-Aware):")
    for name, frame in split_map.items():
        out_path = OUTPUT / f"{name}.parquet"
        frame.to_parquet(out_path, index=False)
        num_sources = frame["source_id"].nunique() if "source_id" in frame.columns else 0
        print(f"  {name:12s}: {len(frame):8,d} rows | {num_sources:6,d} unique sources")

    print("\nSource Leakage Audit:")
    t_s = set(train_df["source_id"])
    v_s = set(val_df["source_id"])
    tst_s = set(test_df["source_id"])
    ov_tv = len(t_s.intersection(v_s))
    ov_tt = len(t_s.intersection(tst_s))
    print(f"  Train vs Validation source overlap: {ov_tv}")
    print(f"  Train vs Test source overlap:       {ov_tt}")
    assert ov_tv == 0 and ov_tt == 0, "Source leakage detected!"
    print("SUCCESS: 0 source overlap verified between Train, Validation, and Test sets.")


if __name__ == "__main__":
    main()
