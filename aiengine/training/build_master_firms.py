from pathlib import Path
import re

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent

RAW_DIR = (
    BASE_DIR
    / "datasets"
    / "raw"
)

OUTPUT_DIR = (
    BASE_DIR
    / "datasets"
    / "processed"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT = (
    OUTPUT_DIR
    / "firms_master.parquet"
)


# ---------------------------------------------------------
# ONLY STANDARD-PROCESSING DATASETS FOR TRAINING
# ---------------------------------------------------------

STANDARD_SOURCES = {
    "viirs_noaa20_sp": "VIIRS_NOAA20_SP",
    "viirs_noaa21_sp": "VIIRS_NOAA21_SP",
}


def find_year_from_filename(
    filename: str
):
    """
    Extract four-digit year from filenames such as:
    firms_raw_2018.csv
    firms_raw_2026.csv
    """

    match = re.search(
        r"(20\d{2})",
        filename
    )

    if not match:
        return None

    return int(
        match.group(1)
    )


def discover_files():

    discovered = []

    for folder, source_name in (
        STANDARD_SOURCES.items()
    ):

        source_dir = (
            RAW_DIR
            / folder
        )

        if not source_dir.exists():

            print(
                f"WARNING: missing directory "
                f"{source_dir}"
            )

            continue

        # Recursive search.
        # This handles year folders too.
        files = sorted(
            source_dir.rglob(
                "*.csv"
            )
        )

        for file in files:

            year = (
                find_year_from_filename(
                    file.name
                )
            )

            discovered.append(
                {
                    "path": file,
                    "source": source_name,
                    "year": year,
                }
            )

    return discovered


def read_one_file(
    item
):

    path = item["path"]

    print(
        f"Reading: {path}"
    )

    df = pd.read_csv(
        path
    )

    if df.empty:

        print(
            "  Empty file"
        )

        return None

    df["training_source"] = (
        item["source"]
    )

    df["source_year"] = (
        item["year"]
    )

    df["source_file"] = (
        str(path)
    )

    return df


def main():

    files = discover_files()

    if not files:

        raise RuntimeError(
            "No NOAA-20 SP or NOAA-21 SP "
            "CSV files found."
        )

    print()
    print(
        "=" * 70
    )
    print(
        "DISCOVERED FIRMS FILES"
    )
    print(
        "=" * 70
    )

    for item in files:

        print(
            f"{item['source']:20s}"
            f"year={item['year']}  "
            f"{item['path']}"
        )

    frames = []

    for item in files:

        frame = read_one_file(
            item
        )

        if frame is not None:

            frames.append(
                frame
            )

    if not frames:

        raise RuntimeError(
            "All discovered FIRMS files are empty."
        )

    master = pd.concat(
        frames,
        ignore_index=True
    )

    print()
    print(
        f"Raw combined rows: "
        f"{len(master)}"
    )

    # -----------------------------------------------------
    # Basic normalization
    # -----------------------------------------------------

    master["latitude"] = pd.to_numeric(
        master["latitude"],
        errors="coerce"
    )

    master["longitude"] = pd.to_numeric(
        master["longitude"],
        errors="coerce"
    )

    master["frp"] = pd.to_numeric(
        master["frp"],
        errors="coerce"
    )

    master["brightness"] = pd.to_numeric(
        master["bright_ti4"],
        errors="coerce"
    )

    master["bright_t31"] = pd.to_numeric(
        master["bright_ti5"],
        errors="coerce"
    )

    master["day_night"] = (
        master["daynight"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    master["day_night_numeric"] = (
        master["day_night"] == "N"
    ).astype(float)

    master["firms_type"] = pd.to_numeric(
        master["type"],
        errors="coerce"
    )

    master["acq_time"] = pd.to_numeric(
        master["acq_time"],
        errors="coerce"
    )

    master["acq_date"] = pd.to_datetime(
        master["acq_date"],
        errors="coerce"
    )

    # -----------------------------------------------------
    # Coordinate + FRP validation
    # -----------------------------------------------------

    master = master[
        master["latitude"].between(
            -90,
            90
        )
        &
        master["longitude"].between(
            -180,
            180
        )
    ]

    master = master[
        master["frp"].notna()
        &
        (master["frp"] >= 0)
    ]

    master = master[
        master["acq_date"].notna()
        &
        master["acq_time"].notna()
    ]

    # -----------------------------------------------------
    # Validate HHMM
    # -----------------------------------------------------

    master["acq_time"] = (
        master["acq_time"]
        .astype(int)
    )

    hours = (
        master["acq_time"] // 100
    )

    minutes = (
        master["acq_time"] % 100
    )

    valid_time = (
        hours.between(
            0,
            23
        )
        &
        minutes.between(
            0,
            59
        )
    )

    master = master[
        valid_time
    ]

    # -----------------------------------------------------
    # Acquisition timestamp
    # -----------------------------------------------------

    master["acquired_at"] = (
        master["acq_date"]
        + pd.to_timedelta(
            hours,
            unit="h"
        )
        + pd.to_timedelta(
            minutes,
            unit="m"
        )
    )

    # -----------------------------------------------------
    # Confidence normalization
    # -----------------------------------------------------

    master["confidence"] = (
        master["confidence"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    confidence_map = {
        "l": 0.33,
        "n": 0.66,
        "h": 1.00,
        "low": 0.33,
        "nominal": 0.66,
        "high": 1.00,
    }

    master["confidence_score"] = (
        master["confidence"]
        .map(
            confidence_map
        )
    )

    # -----------------------------------------------------
    # Stable event ID
    # -----------------------------------------------------

    master["satellite"] = (
        master["satellite"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    master["event_id"] = (
        master["satellite"]
        + "_"
        + master["latitude"]
            .round(5)
            .astype(str)
        + "_"
        + master["longitude"]
            .round(5)
            .astype(str)
        + "_"
        + master["acquired_at"]
            .dt.strftime(
                "%Y%m%d%H%M"
            )
            .astype(str)
    )

    before_dedup = len(master)

    master = master.drop_duplicates(
        subset=[
            "event_id"
        ]
    )

    duplicates_removed = (
        before_dedup
        - len(master)
    )

    # -----------------------------------------------------
    # Chronological sort
    # -----------------------------------------------------

    master = master.sort_values(
        "acquired_at"
    ).reset_index(
        drop=True
    )

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    master.to_parquet(
        OUTPUT,
        index=False
    )

    print()
    print(
        "=" * 70
    )
    print(
        "MASTER FIRMS DATASET COMPLETE"
    )
    print(
        "=" * 70
    )

    print(
        f"Files processed: {len(files)}"
    )

    print(
        f"Rows after cleaning: "
        f"{len(master)}"
    )

    print(
        f"Duplicates removed: "
        f"{duplicates_removed}"
    )

    print(
        f"Date range: "
        f"{master['acquired_at'].min()}"
        f" → "
        f"{master['acquired_at'].max()}"
    )

    print()
    print(
        "Rows by source:"
    )

    print(
        master[
            "training_source"
        ]
        .value_counts()
    )

    print()
    print(
        "Rows by year:"
    )

    print(
        master[
            "source_year"
        ]
        .value_counts()
        .sort_index()
    )

    print()
    print(
        f"Saved:\n{OUTPUT}"
    )


if __name__ == "__main__":
    main()