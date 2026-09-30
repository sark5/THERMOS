from pathlib import Path
import pandas as pd
import pyarrow.parquet as parquet


ROOT = Path(__file__).resolve().parent

INPUT = (
    ROOT
    / "datasets"
    / "processed"
    / "firms_temporal_enriched.parquet"
)

OUTPUT = (
    ROOT
    / "datasets"
    / "processed"
    / "thermal_sources.parquet"
)


def main():
    print("=" * 70)
    print("THERMOS — THERMAL SOURCE TABLE")
    print("=" * 70)
    if not INPUT.exists():
        raise FileNotFoundError(
            f"Temporal dataset not found: {INPUT}\n"
            "Run build_temporal_features.py first."
        )

    source_columns = [
        "source_id",
        "facility_id",
        "facility_name",
        "facility_type",

        "distance_to_facility",
        "inside_facility_boundary",

        "industrial_context",
        "mining_context",

        "observation_count",
        "active_days",

        "first_seen",
        "last_seen",

        "mean_frp",
        "median_frp",
        "std_frp",
        "min_frp",
        "max_frp",
        "frp_cv",

        "mean_gap_days",
        "median_gap_days",
        "max_gap_days",

        "longest_active_run",

        "frp_spike_score",
        "max_spike_ratio",
        "high_spike_count",

        "persistence_score",
        "stability_score",
        "anomaly_score",
        "periodicity_score",
        "temporal_growth_score",
    ]

    available_columns = parquet.read_schema(INPUT).names

    existing = [
        c for c in source_columns
        if c in available_columns
    ]

    df = pd.read_parquet(
        INPUT,
        columns=existing,
        engine="pyarrow",
    )

    sources = (
        df[existing]
        .sort_values(
            [
                "source_id",
                "observation_count"
            ],
            ascending=[
                True,
                False
            ]
        )
        .drop_duplicates(
            subset=["source_id"]
        )
        .reset_index(drop=True)
    )

    sources.to_parquet(
        OUTPUT,
        index=False
    )

    print(
        f"\nThermal sources: "
        f"{len(sources):,}"
    )

    print(
        f"\nSaved:\n{OUTPUT}"
    )

    print("\nTop persistent sources:")

    print(
        sources[
            [
                "source_id",
                "observation_count",
                "active_days",
                "mean_frp",
                "persistence_score",
                "stability_score",
                "anomaly_score",
            ]
        ]
        .sort_values(
            "persistence_score",
            ascending=False
        )
        .head(20)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()