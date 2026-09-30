"""
THERMOS Candidate Label Generator (Chunked & Vectorized)
Applies Weak-Label Engine V2 across canonical feature matrix in 100k chunks.
"""

from pathlib import Path
import pandas as pd
import numpy as np
from label_engine_v2 import classify_row

ROOT = Path(__file__).resolve().parent
INPUT_MATRIX = ROOT / "datasets" / "processed" / "firms_canonical_matrix.parquet"
OUTPUT_LABELS = ROOT / "datasets" / "processed" / "firms_labeled.parquet"

CHUNK_SIZE = 100_000


def main():
    print("=" * 70)
    print("THERMOS — CANDIDATE LABEL GENERATION")
    print("=" * 70)

    if not INPUT_MATRIX.exists():
        raise FileNotFoundError(f"Input canonical matrix not found: {INPUT_MATRIX}")

    print(f"Loading canonical matrix from {INPUT_MATRIX}...")
    df = pd.read_parquet(INPUT_MATRIX)
    total_rows = len(df)
    print(f"Total rows to classify: {total_rows:,}")

    thermos_labels = []
    label_scores = []
    label_margins = []
    label_qualities = []

    print("Executing Weak-Label Engine V2 in 100k chunks...")
    for start in range(0, total_rows, CHUNK_SIZE):
        end = min(start + CHUNK_SIZE, total_rows)
        chunk = df.iloc[start:end]
        chunk_dict = chunk.to_dict(orient="records")
        for row in chunk_dict:
            res = classify_row(row)
            thermos_labels.append(res["thermos_label"])
            label_scores.append(res["label_score"])
            label_margins.append(res["label_margin"])
            label_qualities.append(res["label_quality"])
        if (start // CHUNK_SIZE) % 10 == 0:
            print(f"  Processed {end:,} / {total_rows:,} rows...")

    df["thermos_label"] = thermos_labels
    df["label_score"] = label_scores
    df["label_margin"] = label_margins
    df["label_quality"] = label_qualities
    df["gold_label"] = df["thermos_label"]

    OUTPUT_LABELS.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUTPUT_LABELS, index=False)

    print("\n" + "=" * 70)
    print("LABEL GENERATION COMPLETE")
    print("=" * 70)
    print(f"Saved labeled dataset to: {OUTPUT_LABELS}")
    print("\nClass Distribution:")
    print(df["gold_label"].value_counts().to_string())
    print("\nLabel Quality Breakdown:")
    print(df["label_quality"].value_counts().to_string())


if __name__ == "__main__":
    main()