from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = (
    Path(__file__).resolve().parent
)

INPUT = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "firms_master.parquet"
)

OUTPUT = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "firms_temporal.parquet"
)


def _rolling_window_stats(group):
    """Compute rolling statistics with vectorized cumulative sums for one cell."""

    ordered = group.sort_values(
        "acquired_at",
        kind="mergesort",
    ).copy()

    timestamps = ordered["acquired_at"].to_numpy(dtype="datetime64[ns]")
    timestamp_ns = timestamps.astype("int64")
    values = ordered["historical_frp"].to_numpy(dtype="float64")

    windows = {
        "mean_frp_30d": pd.Timedelta("30D"),
        "std_frp_30d": pd.Timedelta("30D"),
        "mean_frp_90d": pd.Timedelta("90D"),
        "mean_frp_365d": pd.Timedelta("365D"),
    }

    stats = {
        "mean_frp_30d": np.full(len(ordered), np.nan, dtype=float),
        "std_frp_30d": np.full(len(ordered), np.nan, dtype=float),
        "mean_frp_90d": np.full(len(ordered), np.nan, dtype=float),
        "mean_frp_365d": np.full(len(ordered), np.nan, dtype=float),
    }

    valid = np.isfinite(values)
    numeric_values = np.where(valid, values, 0.0)
    cumulative_sum = np.concatenate(([0.0], np.cumsum(numeric_values)))
    cumulative_square_sum = np.concatenate(
        ([0.0], np.cumsum(numeric_values * numeric_values))
    )
    cumulative_count = np.concatenate(([0], np.cumsum(valid, dtype=np.int64)))
    row_positions = np.arange(len(ordered), dtype=np.int64)
    right = row_positions + 1

    for name, window in windows.items():
        left = np.searchsorted(
            timestamp_ns,
            timestamp_ns - window.value,
            side="right",
        )

        sums = cumulative_sum[right] - cumulative_sum[left]
        counts = cumulative_count[right] - cumulative_count[left]
        means = np.full(len(ordered), np.nan, dtype=float)
        has_values = counts > 0
        means[has_values] = sums[has_values] / counts[has_values]

        if name.startswith("std"):
            square_sums = (
                cumulative_square_sum[right]
                - cumulative_square_sum[left]
            )
            has_variance = counts > 1
            variance = np.full(len(ordered), np.nan, dtype=float)
            variance[has_variance] = (
                square_sums[has_variance]
                - (sums[has_variance] ** 2 / counts[has_variance])
            ) / (counts[has_variance] - 1)
            stats[name] = np.sqrt(np.maximum(variance, 0.0))
        else:
            stats[name] = means

    return ordered.index.to_numpy(), stats


def build_features(
    df
):

    df = df.copy()

    df["acquired_at"] = pd.to_datetime(
        df["acquired_at"],
        utc=True
    )

    df = df.sort_values(
        [
            "latitude",
            "longitude",
            "acquired_at"
        ]
    )

    # --------------------------------------------------
    # Approximate spatial cell.
    #
    # This gives us a repeatable local history key.
    # Source-level clustering will be added later.
    # --------------------------------------------------

    df["grid_lat"] = (
        df["latitude"]
        .round(3)
    )

    df["grid_lon"] = (
        df["longitude"]
        .round(3)
    )

    group_columns = [
        "grid_lat",
        "grid_lon"
    ]

    grouped = df.groupby(
        group_columns
    )

    # --------------------------------------------------
    # Previous observation
    # --------------------------------------------------

    df["previous_frp"] = (
        grouped["frp"]
        .shift(1)
    )

    df["previous_time"] = (
        grouped["acquired_at"]
        .shift(1)
    )

    df["hours_since_previous"] = (
        (
            df["acquired_at"]
            - df["previous_time"]
        )
        .dt.total_seconds()
        / 3600.0
    )

    # --------------------------------------------------
    # FRP difference
    # --------------------------------------------------

    df["frp_change"] = (
        df["frp"]
        - df["previous_frp"]
    )

    df["frp_change_ratio"] = (
        df["frp_change"]
        / df[
            "previous_frp"
        ].replace(
            0,
            np.nan
        )
    )

    # --------------------------------------------------
    # Rolling statistics.
    #
    # Shift first so current observation doesn't
    # contaminate its own historical baseline.
    # --------------------------------------------------

    shifted = (
        grouped["frp"]
        .shift(1)
    )

    temp = df[
        [
            "grid_lat",
            "grid_lon",
            "acquired_at",
        ]
    ].copy()

    temp["historical_frp"] = shifted
    temp = temp.sort_values(
        [
            "grid_lat",
            "grid_lon",
            "acquired_at",
        ]
    )

    for column in [
        "mean_frp_30d",
        "std_frp_30d",
        "mean_frp_90d",
        "mean_frp_365d",
    ]:
        df[column] = np.nan

    for _, group in temp.groupby(
        ["grid_lat", "grid_lon"],
        sort=False,
        dropna=False,
    ):
        hist_index, stats = _rolling_window_stats(group)
        for column, values in stats.items():
            df.loc[hist_index, column] = values

    # --------------------------------------------------
    # Anomaly against 30-day historical baseline.
    # --------------------------------------------------

    safe_std = (
        df[
            "std_frp_30d"
        ]
        .replace(
            0,
            np.nan
        )
    )

    df["historical_zscore"] = (
        (
            df["frp"]
            - df["mean_frp_30d"]
        )
        / safe_std
    )

    df[
        "historical_zscore"
    ] = (
        df[
            "historical_zscore"
        ]
        .replace(
            [np.inf, -np.inf],
            np.nan
        )
        .fillna(0)
    )

    df["anomaly_score"] = (
        df[
            "historical_zscore"
        ]
        .clip(
            0,
            5
        )
        / 5.0
    )

    # --------------------------------------------------
    # Long-term persistence.
    # --------------------------------------------------

    counts = (
        grouped["frp"]
        .transform("count")
    )

    df["observation_count_local"] = (
        counts
    )

    return df


def main():

    df = pd.read_parquet(
        INPUT
    )

    print(
        f"Input rows: {len(df)}"
    )

    result = build_features(
        df
    )

    result.to_parquet(
        OUTPUT,
        index=False
    )

    print(
        f"Saved: {OUTPUT}"
    )

    print(
        f"Columns: {len(result.columns)}"
    )


if __name__ == "__main__":
    main()