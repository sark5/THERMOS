from pathlib import Path

import pandas as pd


BASE_DIR = (
    Path(__file__).resolve().parent
)

INPUT = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "review_queue.parquet"
)

OUTPUT = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "review_queue.csv"
)


DISPLAY_COLUMNS = [
    "event_id",
    "source_id",

    "latitude",
    "longitude",
    "acquired_at",

    "frp",
    "bright_ti4",
    "bright_ti5",
    "confidence_score",

    "firms_type",

    "facility_name",
    "facility_type",
    "criticality",
    "distance_to_facility",
    "industrial_context",

    "observation_count_30d",
    "active_days_30d",
    "mean_frp_30d",
    "stddev_frp_30d",
    "persistence_score",
    "anomaly_score",

    "worldcover_class_name",
    "tree_fraction",
    "cropland_fraction",
    "builtup_fraction",

    "sentinel2_available",
    "sentinel2_quality_score",

    "ndvi_mean",
    "ndmi_mean",

    "thermos_label",
    "label_score",
    "label_reasons",

    "human_label",
    "review_status",
    "reviewer",
    "review_notes",
    "reviewed_at",
]


def main():

    df = pd.read_parquet(
        INPUT
    )

    columns = [
        column
        for column in DISPLAY_COLUMNS
        if column in df.columns
    ]

    df[
        columns
    ].to_csv(
        OUTPUT,
        index=False
    )

    print(
        f"Exported: {OUTPUT}"
    )

    print(
        f"Rows: {len(df)}"
    )


if __name__ == "__main__":
    main()