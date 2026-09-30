from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent

INPUT = (
    ROOT
    / "datasets"
    / "processed"
    / "firms_spatial_enriched.parquet"
)

EVENT_OUTPUT = (
    ROOT
    / "datasets"
    / "processed"
    / "firms_temporal_enriched.parquet"
)

SOURCE_OUTPUT = (
    ROOT
    / "datasets"
    / "processed"
    / "thermal_sources.parquet"
)


# ============================================================
# ONLY LOAD WHAT THIS STAGE NEEDS
# ============================================================

EVENT_COLUMNS = [
    "latitude",
    "longitude",
    "bright_ti4",
    "scan",
    "track",
    "acq_date",
    "acq_time",
    "satellite",
    "confidence",
    "bright_ti5",
    "frp",
    "daynight",
    "type",
    "training_source",
    "source_year",
    "source_file",
    "acquired_at",
    "confidence_score",
    "event_id",

    "facility_id",
    "osm_id",
    "facility_name",
    "facility_type",
    "operator",
    "distance_to_facility",
    "inside_facility_boundary",
    "industrial_context",
    "mining_context",
]


# ============================================================
# SOURCE ID
# ============================================================

def build_source_id(df: pd.DataFrame) -> pd.Series:
    """
    Fast deterministic first-pass thermal source ID.

    A source is primarily represented by:
      facility context + ~1 km spatial cell

    This is a candidate grouping method, not the final
    scientific source-tracking algorithm.
    """

    grid_lat = np.floor(
        df["latitude"].astype("float64") / 0.01
    ).astype("int32")

    grid_lon = np.floor(
        df["longitude"].astype("float64") / 0.01
    ).astype("int32")

    facility = (
        df["facility_id"]
        .fillna(-1)
        .astype("int64")
        .astype(str)
    )

    return (
        "TS_"
        + facility
        + "_"
        + grid_lat.astype(str)
        + "_"
        + grid_lon.astype(str)
    )


# ============================================================
# SOURCE STATISTICS
# ============================================================

def build_source_statistics(df: pd.DataFrame):
    print("\n[1/5] Building source IDs...")

    df["source_id"] = build_source_id(df)

    print(
        f"Unique thermal sources: "
        f"{df['source_id'].nunique():,}"
    )

    # --------------------------------------------------------
    # Basic source aggregation
    # --------------------------------------------------------

    print("\n[2/5] Computing source statistics...")

    g = df.groupby(
        "source_id",
        sort=False,
        observed=True,
    )

    source = g.agg(
        latitude=("latitude", "mean"),
        longitude=("longitude", "mean"),

        first_seen=("acquired_at", "min"),
        last_seen=("acquired_at", "max"),

        observation_count=("event_id", "count"),

        active_days=(
            "acquired_at",
            lambda x: x.dt.normalize().nunique(),
        ),

        mean_frp=("frp", "mean"),
        median_frp=("frp", "median"),
        max_frp=("frp", "max"),
        min_frp=("frp", "min"),
        frp_stddev=("frp", "std"),

        facility_id=("facility_id", "first"),
        facility_name=("facility_name", "first"),
        facility_type=("facility_type", "first"),
        operator=("operator", "first"),

        distance_to_facility=(
            "distance_to_facility",
            "min",
        ),

        inside_facility_boundary=(
            "inside_facility_boundary",
            "max",
        ),

        industrial_context=(
            "industrial_context",
            "max",
        ),

        mining_context=(
            "mining_context",
            "max",
        ),
    )

    source["frp_stddev"] = (
        source["frp_stddev"]
        .fillna(0.0)
    )

    # --------------------------------------------------------
    # Time span
    # --------------------------------------------------------

    span_days = (
        (
            source["last_seen"]
            - source["first_seen"]
        )
        .dt.total_seconds()
        / 86400.0
    )

    source["span_days"] = (
        span_days
        .clip(lower=1.0)
    )

    source["active_day_ratio"] = (
        source["active_days"]
        / source["span_days"]
    ).clip(0.0, 1.0)

    # --------------------------------------------------------
    # FRP variation
    # --------------------------------------------------------

    source["frp_cv"] = (
        source["frp_stddev"]
        /
        source["mean_frp"]
        .abs()
        .clip(lower=1e-6)
    )

    source["frp_cv"] = (
        source["frp_cv"]
        .replace(
            [np.inf, -np.inf],
            np.nan,
        )
        .fillna(0.0)
    )

    return df, source


# ============================================================
# TEMPORAL GAPS
# ============================================================

def add_gap_features(df: pd.DataFrame, source: pd.DataFrame):

    print("\n[3/5] Computing temporal gaps...")

    # Only one timestamp column needed.
    work = df[
        [
            "source_id",
            "acquired_at",
        ]
    ].copy()

    work.sort_values(
        [
            "source_id",
            "acquired_at",
        ],
        inplace=True,
    )

    previous = (
        work.groupby(
            "source_id",
            sort=False,
            observed=True,
        )["acquired_at"]
        .shift(1)
    )

    gap_days = (
        (
            work["acquired_at"]
            - previous
        )
        .dt.total_seconds()
        / 86400.0
    )

    work["gap_days"] = gap_days

    gap_stats = (
        work.groupby(
            "source_id",
            sort=False,
            observed=True,
        )["gap_days"]
        .agg(
            mean_gap_days="mean",
            median_gap_days="median",
            max_gap_days="max",
        )
    )

    source = source.join(
        gap_stats,
        how="left",
    )

    source[
        [
            "mean_gap_days",
            "median_gap_days",
            "max_gap_days",
        ]
    ] = (
        source[
            [
                "mean_gap_days",
                "median_gap_days",
                "max_gap_days",
            ]
        ]
        .fillna(0.0)
    )

    return source


# ============================================================
# SCORE CALCULATION
# ============================================================

def calculate_scores(source: pd.DataFrame):

    print("\n[4/5] Computing behavioral scores...")

    # --------------------------------------------------------
    # Persistence
    # --------------------------------------------------------

    persistence = (
        0.55
        * source["active_day_ratio"]
        +
        0.30
        * np.clip(
            source["active_days"] / 365.0,
            0.0,
            1.0,
        )
        +
        0.15
        * np.clip(
            source["observation_count"] / 100.0,
            0.0,
            1.0,
        )
    )

    source["persistence_score"] = np.clip(
        persistence,
        0.0,
        1.0,
    )

    # --------------------------------------------------------
    # Stability
    # --------------------------------------------------------

    source["stability_score"] = (
        1.0
        /
        (
            1.0
            + source["frp_cv"]
        )
    ).clip(0.0, 1.0)

    # --------------------------------------------------------
    # Fast anomaly proxy
    #
    # We intentionally avoid rolling/FFT over 1.55M groups.
    # --------------------------------------------------------

    intensity_ratio = (
        source["max_frp"]
        /
        source["mean_frp"]
        .abs()
        .clip(lower=1e-6)
    )

    intensity_anomaly = (
        (intensity_ratio - 1.0)
        / 9.0
    ).clip(0.0, 1.0)

    source["anomaly_score"] = (
        0.70 * intensity_anomaly
        +
        0.30 * (
            1.0
            - source["stability_score"]
        )
    ).clip(0.0, 1.0)

    # --------------------------------------------------------
    # Persistence × stability signal
    #
    # Particularly useful for flare candidates.
    # --------------------------------------------------------

    source["flare_signature_score"] = (
        source["persistence_score"]
        *
        source["stability_score"]
    ).clip(0.0, 1.0)

    return source


# ============================================================
# EVENT-LEVEL FEATURES
# ============================================================

def add_event_features(
    df: pd.DataFrame,
    source: pd.DataFrame,
):

    print("\n[5/5] Creating event-level temporal features...")

    # Source-level columns used by downstream ML.
    source_features = [
        "source_id",
        "observation_count",
        "active_days",
        "span_days",
        "active_day_ratio",
        "mean_frp",
        "median_frp",
        "max_frp",
        "min_frp",
        "frp_stddev",
        "frp_cv",
        "mean_gap_days",
        "median_gap_days",
        "max_gap_days",
        "persistence_score",
        "stability_score",
        "anomaly_score",
        "flare_signature_score",
    ]

    # --------------------------------------------------------
    # Event-to-source FRP ratio
    # --------------------------------------------------------

    df.sort_values(
        [
            "source_id",
            "acquired_at",
        ],
        inplace=True,
    )

    previous_frp = (
        df.groupby(
            "source_id",
            sort=False,
            observed=True,
        )["frp"]
        .shift(1)
    )

    df["previous_frp"] = previous_frp

    df["event_frp_ratio"] = (
        df["frp"]
        /
        previous_frp
        .replace(0, np.nan)
    )

    df["event_frp_ratio"] = (
        df["event_frp_ratio"]
        .replace(
            [np.inf, -np.inf],
            np.nan,
        )
        .fillna(1.0)
    )

    df["event_spike_score"] = (
        (
            df["event_frp_ratio"]
            - 1.0
        )
        / 9.0
    ).clip(0.0, 1.0)

    # --------------------------------------------------------
    # Merge source features
    # --------------------------------------------------------

    merge_features = (
        source[source_features]
        .reset_index()
    )

    df = df.merge(
        merge_features,
        on="source_id",
        how="left",
        sort=False,
        validate="many_to_one",
    )

    return df


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("THERMOS — FAST TEMPORAL FINGERPRINT ENGINE")
    print("=" * 70)

    if not INPUT.exists():
        raise FileNotFoundError(
            f"Input not found:\n{INPUT}"
        )

    # --------------------------------------------------------
    # Read only relevant columns
    # --------------------------------------------------------

    print("\nReading FIRMS spatial dataset...")

    df = pd.read_parquet(
        INPUT,
        columns=EVENT_COLUMNS,
    )

    print(
        f"Input observations: "
        f"{len(df):,}"
    )

    # --------------------------------------------------------
    # Types
    # --------------------------------------------------------

    df["acquired_at"] = pd.to_datetime(
        df["acquired_at"],
        utc=True,
        errors="coerce",
    )

    numeric = [
        "latitude",
        "longitude",
        "bright_ti4",
        "bright_ti5",
        "frp",
        "confidence_score",
        "distance_to_facility",
        "industrial_context",
        "mining_context",
    ]

    for col in numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce",
            )

    # --------------------------------------------------------
    # Build source statistics
    # --------------------------------------------------------

    df, source = build_source_statistics(df)

    # --------------------------------------------------------
    # Temporal gaps
    # --------------------------------------------------------

    source = add_gap_features(
        df,
        source,
    )

    # --------------------------------------------------------
    # Scores
    # --------------------------------------------------------

    source = calculate_scores(
        source
    )

    # --------------------------------------------------------
    # Event features
    # --------------------------------------------------------

    df = add_event_features(
        df,
        source,
    )

    # --------------------------------------------------------
    # Save source table
    # --------------------------------------------------------

    print("\nWriting thermal_sources.parquet...")

    source.reset_index().to_parquet(
        SOURCE_OUTPUT,
        index=False,
        compression="snappy",
    )

    # --------------------------------------------------------
    # Save event table
    # --------------------------------------------------------

    print(
        "\nWriting firms_temporal_enriched.parquet..."
    )

    df.sort_values(
        "acquired_at",
        inplace=True,
    )

    df.to_parquet(
        EVENT_OUTPUT,
        index=False,
        compression="snappy",
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("TEMPORAL FEATURE ENGINE COMPLETE")
    print("=" * 70)

    print(
        f"\nObservations: "
        f"{len(df):,}"
    )

    print(
        f"Thermal sources: "
        f"{len(source):,}"
    )

    print(
        f"\nEvent output:\n"
        f"{EVENT_OUTPUT}"
    )

    print(
        f"\nSource output:\n"
        f"{SOURCE_OUTPUT}"
    )

    print("\nSource fingerprint summary:")

    summary_cols = [
        "observation_count",
        "active_days",
        "mean_frp",
        "frp_cv",
        "persistence_score",
        "stability_score",
        "anomaly_score",
        "flare_signature_score",
    ]

    print(
        source[
            summary_cols
        ]
        .describe()
        .round(4)
        .to_string()
    )


if __name__ == "__main__":
    main()