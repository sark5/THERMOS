from pathlib import Path

import numpy as np
import pandas as pd

from clustering.source_cluster import (
    ThermalSourceClusterer
)

from clustering.source_ids import (
    generate_source_id
)


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
)

SATELLITE_INPUT = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "firms_satellite_enriched.parquet"
)

INPUT = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "firms_enriched.parquet"
)

OUTPUT = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "thermal_sources.parquet"
)

OUTPUT_CSV = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "thermal_sources.csv"
)


def prepare_records(df):

    df = df.copy()

    df["acquired_at"] = pd.to_datetime(
        df["acquired_at"],
        utc=True,
        errors="coerce"
    )

    df = df[
        df["acquired_at"].notna()
    ]

    return df


def aggregate_cluster(
    cluster,
    source_id
):

    frame = pd.DataFrame(
        cluster
    )

    frp = pd.to_numeric(
        frame["frp"],
        errors="coerce"
    ).dropna()

    mean_latitude = (
        frame["latitude"]
        .astype(float)
        .mean()
    )

    mean_longitude = (
        frame["longitude"]
        .astype(float)
        .mean()
    )

    source = {
        "source_id": source_id,

        "latitude":
            mean_latitude,

        "longitude":
            mean_longitude,

        "first_seen":
            frame["acquired_at"].min(),

        "last_seen":
            frame["acquired_at"].max(),

        "observation_count":
            len(frame),

        "active_days":
            frame[
                "acquired_at"
            ]
            .dt.date
            .nunique(),

        "mean_frp":
            float(
                frp.mean()
            )
            if not frp.empty
            else 0.0,

        "median_frp":
            float(
                frp.median()
            )
            if not frp.empty
            else 0.0,

        "max_frp":
            float(
                frp.max()
            )
            if not frp.empty
            else 0.0,

        "min_frp":
            float(
                frp.min()
            )
            if not frp.empty
            else 0.0,

        "frp_stddev":
            float(
                frp.std(
                    ddof=0
                )
            )
            if not frp.empty
            else 0.0,
    }

    # Take most common facility.
    if (
        "facility_id" in frame.columns
    ):

        facility_values = (
            frame[
                "facility_id"
            ]
            .dropna()
        )

        if not facility_values.empty:

            source[
                "facility_id"
            ] = facility_values.mode().iloc[0]

        else:

            source[
                "facility_id"
            ] = None

    else:

        source[
            "facility_id"
        ] = None

    # Facility metadata.
    for column in [
        "facility_name",
        "facility_type",
        "criticality",
    ]:

        if column in frame.columns:

            values = (
                frame[column]
                .dropna()
                .astype(str)
            )

            source[column] = (
                values.mode().iloc[0]
                if not values.empty
                else None
            )

    return source


def main():

    input_path = (
        SATELLITE_INPUT
        if SATELLITE_INPUT.exists()
        else INPUT
    )

    if not input_path.exists():

        raise FileNotFoundError(
            "Missing input dataset. Expected one of: "
            f"{SATELLITE_INPUT}, {INPUT}"
        )

    df = pd.read_parquet(
        input_path
    )

    if input_path == INPUT:

        print(
            "Satellite-enriched input not found; "
            "using firms_enriched.parquet."
        )

    df = prepare_records(
        df
    )

    records = (
        df.to_dict("records")
    )

    print(
        f"Input observations: "
        f"{len(records)}"
    )

    clusterer = (
        ThermalSourceClusterer(
            distance_meters=1000,
            time_hours=48
        )
    )

    clusters = clusterer.cluster(
        records
    )

    print(
        f"Thermal sources: "
        f"{len(clusters)}"
    )

    sources = []

    event_to_source = {}

    for cluster in clusters:

        source_id = (
            generate_source_id(
                cluster
            )
        )

        source = aggregate_cluster(
            cluster,
            source_id
        )

        sources.append(
            source
        )

        for event in cluster:

            event_to_source[
                event["event_id"]
            ] = source_id

    source_df = pd.DataFrame(
        sources
    )

    source_df.to_parquet(
        OUTPUT,
        index=False
    )

    source_df.to_csv(
        OUTPUT_CSV,
        index=False
    )

    # Save event → source mapping.
    mapping = pd.DataFrame(
        [
            {
                "event_id":
                    event_id,
                "source_id":
                    source_id,
            }
            for event_id, source_id
            in event_to_source.items()
        ]
    )

    mapping_path = (
        BASE_DIR
        / "datasets"
        / "processed"
        / "event_source_mapping.parquet"
    )

    mapping.to_parquet(
        mapping_path,
        index=False
    )

    print()
    print(
        "=" * 60
    )

    print(
        "THERMAL SOURCE CLUSTERING COMPLETE"
    )

    print(
        "=" * 60
    )

    print(
        f"Observations: {len(records)}"
    )

    print(
        f"Sources: {len(source_df)}"
    )

    print(
        f"\nSource dataset: {OUTPUT}"
    )

    print(
        f"Mapping: {mapping_path}"
    )


if __name__ == "__main__":
    main()