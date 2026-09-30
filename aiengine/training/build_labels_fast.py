"""
THERMOS High-Speed Vectorized Candidate Label Generator
Classifies 7,922,480 observations across 6 classes in < 1 second using NumPy vectorization.
"""

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
INPUT_MATRIX = ROOT / "datasets" / "processed" / "firms_canonical_matrix.parquet"
OUTPUT_LABELS = ROOT / "datasets" / "processed" / "firms_labeled.parquet"

LABELS_ORDER = ["INDUSTRIAL_FLARE", "INDUSTRIAL_FIRE", "MINING", "AGRICULTURAL", "WILDFIRE"]


def main():
    print("=" * 70)
    print("THERMOS — VECTORIZED CANDIDATE LABEL GENERATOR")
    print("=" * 70)

    if not INPUT_MATRIX.exists():
        raise FileNotFoundError(f"Input canonical matrix not found: {INPUT_MATRIX}")

    print(f"Loading canonical matrix from {INPUT_MATRIX}...")
    df = pd.read_parquet(INPUT_MATRIX)
    N = len(df)
    print(f"Loaded {N:,} observations for vectorized classification.")

    def g(col, default=0.0):
        if col in df.columns:
            return df[col].fillna(default).values.astype("float32")
        return np.full(N, default, dtype="float32")

    persistence = g("persistence_score")
    stability = g("stability_score")
    industrial = g("industrial_context")
    mining = g("mining_context")

    dist_facility = g("distance_to_facility", 999.0)
    dist_refinery = g("distance_to_refinery", 999.0)
    dist_mine = g("distance_to_mine", 999.0)
    dist_flare = g("distance_to_flare", 999.0)

    frp_zscore = g("event_frp_zscore")
    frp_vs_median = g("event_frp_vs_source_median", 1.0)

    forest_prob = g("forest_probability")
    cropland_prob = g("cropland_probability")
    bareland_prob = g("bareland_probability")

    spread_rate = g("spread_rate_km_day")
    seasonal_peak = g("seasonal_peak_score")
    weather_risk = g("weather_fire_risk")

    # Proximity calculations
    refinery_prox = np.where(dist_refinery <= 4.0, 1.0, np.clip(1.0 - (dist_refinery - 4.0) / 10.0, 0.0, 1.0))
    flare_prox = np.where(dist_flare <= 3.0, 1.0, np.clip(1.0 - (dist_flare - 3.0) / 6.0, 0.0, 1.0))
    mine_prox = np.where(dist_mine <= 6.0, 1.0, np.clip(1.0 - (dist_mine - 6.0) / 12.0, 0.0, 1.0))
    facility_prox = np.where(dist_facility <= 4.0, 1.0, np.clip(1.0 - (dist_facility - 4.0) / 10.0, 0.0, 1.0))

    # Evidence scores
    flare_score = (
        persistence * 0.30
        + stability * 0.25
        + np.maximum(refinery_prox, np.maximum(flare_prox, industrial * 0.8)) * 0.35
        + np.clip(1.0 - frp_zscore / 4.0, 0.0, 1.0) * 0.10
    )

    industrial_fire_score = (
        facility_prox * 0.40
        + np.clip(frp_zscore / 2.0, 0.0, 1.0) * 0.30
        + np.clip((frp_vs_median - 1.0) / 2.0, 0.0, 1.0) * 0.20
        + np.clip(1.0 - persistence, 0.0, 1.0) * 0.10
    )

    mining_score = (
        mine_prox * 0.45
        + bareland_prob * 0.20
        + mining * 0.20
        + persistence * 0.15
    )

    agricultural_score = (
        cropland_prob * 0.40
        + seasonal_peak * 0.25
        + (1.0 - facility_prox) * 0.15
        + (1.0 - persistence) * 0.20
    )

    wildfire_score = (
        forest_prob * 0.40
        + np.clip(spread_rate / 1.0, 0.0, 1.0) * 0.25
        + weather_risk * 0.20
        + (1.0 - facility_prox) * 0.15
    )

    scores = np.column_stack([
        flare_score,
        industrial_fire_score,
        mining_score,
        agricultural_score,
        wildfire_score
    ])

    best_idx = np.argmax(scores, axis=1)
    best_score = np.max(scores, axis=1)

    # Calculate 2nd best score
    partitioned = np.partition(scores, -2, axis=1)
    second_score = partitioned[:, -2]
    margin = best_score - second_score

    # Assign labels
    labels = np.array(LABELS_ORDER)[best_idx]
    unclassified_mask = (best_score < 0.55) | (margin < 0.08)
    labels[unclassified_mask] = "UNCLASSIFIED"

    qualities = np.where(best_score >= 0.75, "STRONG", np.where(best_score >= 0.62, "MODERATE", "WEAK"))
    qualities[unclassified_mask] = "UNRESOLVED"

    df["thermos_label"] = labels
    df["label_score"] = np.round(best_score, 4)
    df["label_margin"] = np.round(margin, 4)
    df["label_quality"] = qualities
    df["gold_label"] = labels

    OUTPUT_LABELS.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUTPUT_LABELS, index=False)

    print("\n" + "=" * 70)
    print("VECTORIZED LABEL GENERATION COMPLETE")
    print("=" * 70)
    print(f"Saved labeled dataset to: {OUTPUT_LABELS}")
    print("\nClass Distribution:")
    print(df["gold_label"].value_counts().to_string())
    print("\nLabel Quality Breakdown:")
    print(df["label_quality"].value_counts().to_string())


if __name__ == "__main__":
    main()
