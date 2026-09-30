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

OUTPUT = (
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
# PERFORMANCE CONFIGURATION
# ============================================================

# Use only columns required by this stage.
REQUIRED_COLUMNS = [
    "event_id",
    "latitude",
    "longitude",
    "acquired_at",
    "frp",
    "facility_id",
    "facility_name",
    "facility_type",
    "distance_to_facility",
    "inside_facility_boundary",
    "industrial_context",
    "mining_context",
]


# ============================================================
# SOURCE ID
# ============================================================

def build_source_ids(df: pd.DataFrame) -> pd.DataFrame:

    print("\nBuilding source IDs...")

    df["grid_lat"] = (
        np.floor(df["latitude"] / 0.01)
        .astype(np.int32)
    )

    df["grid_lon"] = (
        np.floor(df["longitude"] / 0.01)
        .astype(np.int32)
    )

    facility_component = (
        df["facility_id"]
        .fillna(-1)
        .astype("int64")
        .astype(str)
    )

    df["source_id"] = (
        "TS_"
        + facility_component
        + "_"
        + df["grid_lat"].astype(str)
        + "_"
        + df["grid_lon"].astype(str)
    )

    df.drop(
        columns=[
            "grid_lat",
            "grid_lon",
        ],
        inplace=True,
    )

    return df


# ============================================================
# BASIC SOURCE AGGREGATIONS
# ============================================================

def build_basic_statistics(df: pd.DataFrame):

    print("\nCalculating source-level statistics...")

    grouped = df.groupby(
        "source_id",
        sort=False,
        observed=True,
    )

    stats = grouped["frp"].agg(
        observation_count="size",
        mean_frp="mean",
        median_frp="median",
        std_frp="std",
        min_frp="min",
        max_frp="max",
    )

    stats["std_frp"] = (
        stats["std_frp"]
        .fillna(0.0)
    )

    # --------------------------------------------------------
    # Active days
    # --------------------------------------------------------

    daily = (
        df.assign(
            observation_day=df["acquired_at"]
            .dt.floor("D")
        )
        .groupby(
            [
                "source_id",
                "observation_day",
            ],
            sort=False,
            observed=True,
        )
        .agg(
            daily_frp=("frp", "mean")
        )
        .reset_index()
    )

    active_days = (
        daily.groupby(
            "source_id",
            sort=False,
            observed=True,
        )
        .size()
        .rename("active_days")
    )

    stats = stats.join(active_days)

    # --------------------------------------------------------
    # First / last observation
    # --------------------------------------------------------

    times = (
        grouped["acquired_at"]
        .agg(
            first_seen="min",
            last_seen="max",
        )
    )

    stats = stats.join(times)

    # --------------------------------------------------------
    # FRP coefficient of variation
    # --------------------------------------------------------

    stats["frp_cv"] = (
        stats["std_frp"]
        / stats["mean_frp"].abs().clip(lower=1e-9)
    )

    stats["frp_cv"] = (
        stats["frp_cv"]
        .replace(
            [np.inf, -np.inf],
            np.nan,
        )
        .fillna(0.0)
    )

    # --------------------------------------------------------
    # Observation span
    # --------------------------------------------------------

    span_days = (
        (
            stats["last_seen"]
            - stats["first_seen"]
        )
        .dt.total_seconds()
        / 86400.0
    )

    span_days = span_days.clip(lower=1.0)

    stats["observation_span_days"] = span_days

    stats["active_day_ratio"] = (
        stats["active_days"]
        / stats["observation_span_days"]
    )

    stats["active_day_ratio"] = np.clip(
        stats["active_day_ratio"],
        0.0,
        1.0,
    )

    return stats, daily


# ============================================================
# DAILY TEMPORAL FEATURES
# ============================================================

def build_daily_features(daily: pd.DataFrame):

    print("\nBuilding daily temporal features...")

    daily = daily.sort_values(
        ["source_id", "observation_day"]
    )

    daily["active"] = (
        daily["daily_frp"] > 0
    )

    # --------------------------------------------------------
    # Daily FRP rolling median
    #
    # This replaces per-source rolling operations.
    # --------------------------------------------------------

    daily["rolling_median"] = (
        daily.groupby(
            "source_id",
            sort=False,
            observed=True,
        )["daily_frp"]
        .transform(
            lambda x: x.rolling(
                window=7,
                min_periods=2,
            ).median()
        )
    )

    daily["spike_ratio"] = (
        daily["daily_frp"]
        / daily["rolling_median"]
        .replace(0, np.nan)
    )

    daily["spike_ratio"] = (
        daily["spike_ratio"]
        .replace(
            [np.inf, -np.inf],
            np.nan,
        )
        .fillna(0.0)
    )

    # --------------------------------------------------------
    # Maximum spike
    # --------------------------------------------------------

    spike_stats = (
        daily.groupby(
            "source_id",
            sort=False,
            observed=True,
        )["spike_ratio"]
        .agg(
            max_spike_ratio="max",
            high_spike_count=lambda x: (
                x >= 3.0
            ).sum(),
        )
    )

    # --------------------------------------------------------
    # Longest active run
    #
    # Vectorized streak calculation.
    # --------------------------------------------------------

    reset = (
        ~daily["active"]
    )

    groups = (
        reset.groupby(
            daily["source_id"],
            sort=False,
            observed=True,
        )
        .cumsum()
    )

    daily["_run_group"] = groups

    runs = (
        daily[daily["active"]]
        .groupby(
            [
                "source_id",
                "_run_group",
            ],
            sort=False,
            observed=True,
        )
        .size()
    )

    longest_run = (
        runs.groupby(
            level=0,
            sort=False,
        )
        .max()
        .rename("longest_active_run")
    )

    # --------------------------------------------------------
    # Temporal gaps
    # --------------------------------------------------------

    daily["previous_day"] = (
        daily.groupby(
            "source_id",
            sort=False,
            observed=True,
        )["observation_day"]
        .shift(1)
    )

    daily["gap_days"] = (
        (
            daily["observation_day"]
            - daily["previous_day"]
        )
        .dt.total_seconds()
        / 86400.0
    )

    gap_stats = (
        daily.groupby(
            "source_id",
            sort=False,
            observed=True,
        )["gap_days"]
        .agg(
            mean_gap_days="mean",
            median_gap_days="median",
            max_gap_days="max",
        )
        .fillna(0.0)
    )

    # --------------------------------------------------------
    # Daily mean / std
    # --------------------------------------------------------

    daily_stats = (
        daily.groupby(
            "source_id",
            sort=False,
            observed=True,
        )["daily_frp"]
        .agg(
            daily_mean_frp="mean",
            daily_std_frp="std",
        )
        .fillna(0.0)
    )

    # --------------------------------------------------------
    # Combine
    # --------------------------------------------------------

    result = (
        spike_stats
        .join(longest_run, how="outer")
        .join(gap_stats, how="outer")
        .join(daily_stats, how="outer")
    )

    result = result.fillna(0.0)

    return result


# ============================================================
# SOURCE LOCATION / CONTEXT
# ============================================================

def build_context_features(df: pd.DataFrame):

    print("\nBuilding source context...")

    grouped = df.groupby(
        "source_id",
        sort=False,
        observed=True,
    )

    context = grouped.agg(
        latitude=("latitude", "mean"),
        longitude=("longitude", "mean"),

        facility_id=("facility_id", "first"),
        facility_name=("facility_name", "first"),
        facility_type=("facility_type", "first"),

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

    return context


# ============================================================
# DERIVED SCORES
# ============================================================

def calculate_scores(stats):

    print("\nCalculating temporal scores...")

    # --------------------------------------------------------
    # Persistence
    # --------------------------------------------------------

    persistence = (
        0.50
        * stats["active_day_ratio"]
        +
        0.30
        * np.clip(
            stats["active_days"] / 365.0,
            0.0,
            1.0,
        )
        +
        0.20
        * np.clip(
            stats["longest_active_run"] / 30.0,
            0.0,
            1.0,
        )
    )

    stats["persistence_score"] = np.clip(
        persistence,
        0.0,
        1.0,
    )

    # --------------------------------------------------------
    # Stability
    # --------------------------------------------------------

    stats["stability_score"] = (
        1.0
        / (
            1.0
            + stats["frp_cv"]
        )
    )

    stats["stability_score"] = np.clip(
        stats["stability_score"],
        0.0,
        1.0,
    )

    # --------------------------------------------------------
    # FRP spike
    # --------------------------------------------------------

    stats["frp_spike_score"] = np.clip(
        (
            stats["max_spike_ratio"] - 1.0
        )
        / 9.0,
        0.0,
        1.0,
    )

    # --------------------------------------------------------
    # Intensity anomaly
    # --------------------------------------------------------

    intensity_ratio = (
        stats["max_frp"]
        / stats["mean_frp"]
        .abs()
        .clip(lower=1e-9)
    )

    intensity_anomaly = np.clip(
        (intensity_ratio - 1.0) / 9.0,
        0.0,
        1.0,
    )

    # --------------------------------------------------------
    # Combined anomaly
    # --------------------------------------------------------

    stats["anomaly_score"] = np.clip(
        0.6
        * stats["frp_spike_score"]
        +
        0.4
        * intensity_anomaly,
        0.0,
        1.0,
    )

    # --------------------------------------------------------
    # Simple periodicity proxy
    #
    # Instead of running FFT on all 1.55M sources,
    # use observation regularity as a cheap proxy.
    #
    # A proper FFT can be applied later only to selected
    # persistent sources.
    # --------------------------------------------------------

    gap_regularity = (
        1.0
        / (
            1.0
            + stats["mean_gap_days"].abs()
        )
    )

    stats["periodicity_score"] = np.clip(
        gap_regularity,
        0.0,
        1.0,
    )

    return stats


# ============================================================
# EVENT-LEVEL FRP SPIKE
# ============================================================

def add_event_spike_feature(df):

    print("\nAdding event-level spike information...")

    df = df.sort_values(
        ["source_id", "acquired_at"]
    )

    # Previous observation of same source.
    previous_frp = (
        df.groupby(
            "source_id",
            sort=False,
            observed=True,
        )["frp"]
        .shift(1)
    )

    df["event_frp_ratio"] = (
        df["frp"]
        / previous_frp
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

    df["event_spike_score"] = np.clip(
        (
            df["event_frp_ratio"]
            - 1.0
        ) / 9.0,
        0.0,
        1.0,
    )

    return df


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("THERMOS — OPTIMIZED TEMPORAL FINGERPRINT ENGINE")
    print("=" * 70)

    if not INPUT.exists():
        raise FileNotFoundError(
            f"Missing input dataset:\n{INPUT}"
        )

    # --------------------------------------------------------
    # Read only needed columns
    # --------------------------------------------------------

    print("\nReading dataset...")

    available = pd.read_parquet(
        INPUT,
        columns=None,
    ).columns.tolist()

    columns = [
        c
        for c in REQUIRED_COLUMNS
        if c in available
    ]

    df = pd.read_parquet(
        INPUT,
        columns=columns,
    )

    print(
        f"Input observations: "
        f"{len(df):,}"
    )

    # --------------------------------------------------------
    # Optimize dtypes
    # --------------------------------------------------------

    df["acquired_at"] = pd.to_datetime(
        df["acquired_at"],
        utc=True,
        errors="coerce",
    )

    numeric_columns = [
        "latitude",
        "longitude",
        "frp",
        "distance_to_facility",
        "industrial_context",
        "mining_context",
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce",
            )

    # --------------------------------------------------------
    # Source IDs
    # --------------------------------------------------------

    df = build_source_ids(df)

    print(
        f"Thermal sources: "
        f"{df['source_id'].nunique():,}"
    )

    # --------------------------------------------------------
    # Basic statistics
    # --------------------------------------------------------

    source_stats, daily = (
        build_basic_statistics(df)
    )

    # --------------------------------------------------------
    # Daily statistics
    # --------------------------------------------------------

    temporal_stats = (
        build_daily_features(daily)
    )

    # --------------------------------------------------------
    # Context
    # --------------------------------------------------------

    context = build_context_features(df)

    # --------------------------------------------------------
    # Merge source statistics
    # --------------------------------------------------------

    sources = (
        source_stats
        .join(
            temporal_stats,
            how="left",
        )
        .join(
            context,
            how="left",
        )
    )

    # --------------------------------------------------------
    # Fill missing
    # --------------------------------------------------------

    numeric_source_columns = (
        sources
        .select_dtypes(
            include=[np.number]
        )
        .columns
    )

    sources[numeric_source_columns] = (
        sources[numeric_source_columns]
        .replace(
            [np.inf, -np.inf],
            np.nan,
        )
        .fillna(0.0)
    )

    # --------------------------------------------------------
    # Scores
    # --------------------------------------------------------

    sources = calculate_scores(
        sources
    )

    # --------------------------------------------------------
    # Reset index
    # --------------------------------------------------------

    sources.reset_index(
        inplace=True
    )

    # --------------------------------------------------------
    # Event level features
    # --------------------------------------------------------

    df = add_event_spike_feature(df)

    # --------------------------------------------------------
    # Remove duplicated source columns
    # --------------------------------------------------------

    event_features = sources[
        [
            "source_id",
            "observation_count",
            "active_days",
            "first_seen",
            "last_seen",
            "observation_span_days",
            "active_day_ratio",
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
        ]
    ]

    df = df.merge(
        event_features,
        on="source_id",
        how="left",
        sort=False,
    )

    # --------------------------------------------------------
    # Sort final event data
    # --------------------------------------------------------

    df.sort_values(
        "acquired_at",
        inplace=True,
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    print("\nSaving event-level dataset...")

    df.to_parquet(
        OUTPUT,
        index=False,
        compression="snappy",
    )

    print("Saving source-level dataset...")

    sources.to_parquet(
        SOURCE_OUTPUT,
        index=False,
        compression="snappy",
    )

    # --------------------------------------------------------
    # Report
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("TEMPORAL FINGERPRINT COMPLETE")
    print("=" * 70)

    print(
        f"\nEvent rows: "
        f"{len(df):,}"
    )

    print(
        f"Thermal sources: "
        f"{len(sources):,}"
    )

    print(
        f"\nEvent dataset:\n{OUTPUT}"
    )

    print(
        f"\nSource dataset:\n{SOURCE_OUTPUT}"
    )

    print("\nKey source features:")

    print(
        sources[
            [
                "persistence_score",
                "stability_score",
                "anomaly_score",
                "frp_spike_score",
                "periodicity_score",
            ]
        ]
        .describe()
        .round(4)
        .to_string()
    )


if __name__ == "__main__":
    main()