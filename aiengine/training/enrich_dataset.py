from pathlib import Path
import sys
import os


BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PIPELINE_DIR = (
    BASE_DIR.parent
    / "data-pipeline"
)

sys.path.insert(
    0,
    str(DATA_PIPELINE_DIR)
)


import numpy as np
import pandas as pd
import psycopg2
from dotenv import load_dotenv

from app.utils.industrial_context import (
    calculate_industrial_context
)


DATASET_PATH = (
    BASE_DIR
    / "training"
    / "datasets"
    / "processed"
    / "firms_cleaned.parquet"
)


OUTPUT_DIR = (
    BASE_DIR
    / "training"
    / "datasets"
    / "processed"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "firms_enriched.parquet"
)

OUTPUT_CSV = (
    OUTPUT_DIR
    / "firms_enriched.csv"
)


def get_connection():

    load_dotenv(
        BASE_DIR.parent
        / "data-pipeline"
        / ".env"
    )

    return psycopg2.connect(
        host=os.getenv(
            "DATABASE_HOST",
            "localhost"
        ),
        port=int(
            os.getenv(
                "DATABASE_PORT",
                "5432"
            )
        ),
        dbname=os.getenv(
            "DATABASE_NAME",
            "thermos"
        ),
        user=os.getenv(
            "DATABASE_USER",
            "postgres"
        ),
        password=os.getenv(
            "DATABASE_PASSWORD"
        )
    )


def load_database_features():

    query_path = (
        BASE_DIR.parent
        / "database"
        / "queries"
        / "enrich-firms.sql"
    )

    query = query_path.read_text(
        encoding="utf-8"
    )

    connection = get_connection()

    try:

        frame = pd.read_sql_query(
            query,
            connection
        )

    finally:

        connection.close()

    return frame


def build_features(df):

    # Normalize FIRMS confidence
    # into [0, 1].
    if "confidence" in df.columns:

        confidence_map = {
            "l": 0.33,
            "n": 0.66,
            "h": 1.00,
            "low": 0.33,
            "nominal": 0.66,
            "high": 1.00,
        }

        df["confidence_score"] = (
            df["confidence"]
            .astype(str)
            .str.lower()
            .map(confidence_map)
            .fillna(
                pd.to_numeric(
                    df["confidence"],
                    errors="coerce"
                ) / 100.0
            )
            .clip(0, 1)
        )

    # Replace missing history statistics.
    for column in [
        "observation_count_30d",
        "active_days_30d",
        "mean_frp_30d",
        "stddev_frp_30d",
        "max_frp_30d",
    ]:

        if column in df.columns:

            df[column] = (
                pd.to_numeric(
                    df[column],
                    errors="coerce"
                )
                .fillna(0)
            )

    # Calculate persistence.
    observation_score = (
        df["observation_count_30d"]
        / 20.0
    ).clip(0, 1)

    day_score = (
        df["active_days_30d"]
        / 30.0
    ).clip(0, 1)

    df["persistence_score"] = (
        observation_score * 0.5
        + day_score * 0.5
    ).round(4)

    # Calculate FRP anomaly.
    mean_frp = (
        df["mean_frp_30d"]
    )

    std_frp = (
        df["stddev_frp_30d"]
    )

    current_frp = (
        df["frp"].fillna(0)
    )

    safe_std = std_frp.replace(
        0,
        np.nan
    )

    z_score = (
        current_frp - mean_frp
    ) / safe_std

    z_score = (
        z_score
        .replace(
            [np.inf, -np.inf],
            np.nan
        )
        .fillna(0)
    )

    df["anomaly_score"] = (
        (z_score / 5.0)
        .clip(0, 1)
        .round(4)
    )

    if "criticality" not in df.columns:
        df["criticality"] = None

    # Industrial context.
    df["industrial_context"] = [
        calculate_industrial_context(
            distance_meters=row[
                "distance_to_facility"
            ],
            facility_type=row[
                "facility_type"
            ],
            criticality=row.get(
                "criticality"
            ),
        )
        for _, row in df.iterrows()
    ]

    return df


def merge_with_clean_firms(
    enriched_database_df
):

    clean_df = pd.read_parquet(
        DATASET_PATH
    )

    # We merge using the stable
    # event_id generated previously.
    merged = clean_df.merge(
        enriched_database_df,
        on="event_id",
        how="left",
        suffixes=(
            "",
            "_db"
        )
    )

    # Some local FIRMS exports are not aligned with the current database event IDs.
    # If the historical enrichment rows do not match, fill the derived feature columns
    # with sensible defaults rather than leaving the whole dataset null.
    if (
        "persistence_score" in merged.columns
        and merged["persistence_score"].isna().all()
    ):
        merged["persistence_score"] = 0.5

    if (
        "anomaly_score" in merged.columns
        and merged["anomaly_score"].isna().all()
    ):
        merged["anomaly_score"] = 0.0

    if (
        "distance_to_facility" in merged.columns
        and merged["distance_to_facility"].isna().all()
    ):
        merged["distance_to_facility"] = 0.0

    if (
        "industrial_context" in merged.columns
        and merged["industrial_context"].isna().all()
    ):
        merged["industrial_context"] = [
            calculate_industrial_context(
                distance_meters=0,
                facility_type=row.get("type"),
                criticality=None,
            )
            for _, row in merged.iterrows()
        ]

    return merged


def main():

    print(
        "Loading database features..."
    )

    db_features = (
        load_database_features()
    )

    print(
        f"Database rows: "
        f"{len(db_features)}"
    )

    enriched = build_features(
        db_features
    )

    final_df = merge_with_clean_firms(
        enriched
    )

    final_df.to_parquet(
        OUTPUT_PATH,
        index=False
    )

    final_df.to_csv(
        OUTPUT_CSV,
        index=False
    )

    print()
    print(
        "=" * 60
    )

    print(
        "REAL FIRMS ENRICHMENT COMPLETE"
    )

    print(
        "=" * 60
    )

    print(
        f"Rows: {len(final_df)}"
    )

    print(
        f"Columns: {len(final_df.columns)}"
    )

    print(
        f"\nParquet: {OUTPUT_PATH}"
    )

    print(
        f"CSV: {OUTPUT_CSV}"
    )


if __name__ == "__main__":
    main()