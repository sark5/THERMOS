from pathlib import Path
import time

import pandas as pd

from satellite.sentinel2 import (
    search_sentinel2,
    choose_best_scene,
)

from satellite.worldcover import (
    read_worldcover_window,
    calculate_landcover_statistics,
)

from satellite.context import (
    derive_context_scores,
)


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
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
    / "firms_satellite_enriched.parquet"
)

OUTPUT_CSV = (
    BASE_DIR
    / "datasets"
    / "processed"
    / "firms_satellite_enriched.csv"
)


# Set this to the local WorldCover
# tile path covering your study area.
WORLDCOVER_RASTER = (
    BASE_DIR
    / "satellite_data"
    / "worldcover"
    / "worldcover_2021.tif"
)


def process_worldcover(row):

    if not WORLDCOVER_RASTER.exists():

        return {
            "worldcover_class": None,
            "worldcover_class_name":
                "UNAVAILABLE",
            "tree_fraction": 0.0,
            "cropland_fraction": 0.0,
            "builtup_fraction": 0.0,
            "vegetation_fraction": 0.0,
            "forest_context": 0.0,
            "agricultural_context": 0.0,
            "builtup_context": 0.0,
        }

    data, _ = read_worldcover_window(
        WORLDCOVER_RASTER,
        row["longitude"],
        row["latitude"],
    )

    features = calculate_landcover_statistics(
        data
    )

    context = derive_context_scores(
        features
    )

    return {
        **features,
        **context,
    }


def process_sentinel2(row):

    acquired_at = pd.to_datetime(
        row["acquired_at"],
        utc=True
    ).to_pydatetime()

    try:

        response = search_sentinel2(
            latitude=float(
                row["latitude"]
            ),
            longitude=float(
                row["longitude"]
            ),
            acquisition_time=acquired_at,
        )

        best = choose_best_scene(
            response,
            acquired_at
        )

        if best is None:

            return {
                "sentinel2_available": 0,
                "sentinel2_cloud_cover": 100.0,
                "sentinel2_time_difference_hours":
                    None,
                "sentinel2_quality_score": 0.0,
            }

        return {
            "sentinel2_available": 1,

            "sentinel2_cloud_cover":
                best[
                    "cloud_cover"
                ],

            "sentinel2_time_difference_hours":
                best[
                    "time_difference_hours"
                ],

            "sentinel2_quality_score":
                best[
                    "score"
                ],
        }

    except Exception as error:

        print(
            "Sentinel-2 search failed:",
            error
        )

        return {
            "sentinel2_available": 0,
            "sentinel2_cloud_cover": 100.0,
            "sentinel2_time_difference_hours":
                None,
            "sentinel2_quality_score": 0.0,
        }


def main():

    if not INPUT.exists():

        raise FileNotFoundError(
            INPUT
        )

    df = pd.read_parquet(
        INPUT
    )

    print(
        f"Input rows: {len(df)}"
    )

    results = []

    for index, row in df.iterrows():

        if index % 100 == 0:

            print(
                f"Processing "
                f"{index}/{len(df)}"
            )

        worldcover = (
            process_worldcover(
                row
            )
        )

        sentinel = (
            process_sentinel2(
                row
            )
        )

        results.append({
            **worldcover,
            **sentinel,
        })

        # Avoid hammering the catalogue.
        time.sleep(0.1)

    feature_df = pd.DataFrame(
        results
    )

    final_df = pd.concat(
        [
            df.reset_index(
                drop=True
            ),
            feature_df,
        ],
        axis=1
    )

    final_df.to_parquet(
        OUTPUT,
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
        "SATELLITE ENRICHMENT COMPLETE"
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
        f"Parquet: {OUTPUT}"
    )


if __name__ == "__main__":
    main()