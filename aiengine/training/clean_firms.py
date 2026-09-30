from pathlib import Path
import json
import pandas as pd

from firms_schema import (
    REQUIRED_COLUMNS,
    OPTIONAL_COLUMNS,
    NUMERIC_COLUMNS,
)
from quality_audit import audit_file



BASE_DIR = Path(__file__).resolve().parent

RAW_DIR = BASE_DIR / "datasets" / "raw"

OUTPUT_DIR = BASE_DIR / "datasets" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_raw_files():
    """
    Load all FIRMS raw CSV files from:

        datasets/raw/firms_*/firms_raw.csv

    Returns:
        Combined pandas DataFrame.
    """

    files = list(RAW_DIR.glob("firms_*/firms_raw.csv"))

    if not files:
        raise FileNotFoundError(
            f"No raw FIRMS files found in: {RAW_DIR}"
        )

    frames = []

    for file in files:
        print(f"Loading: {file}")

        frame = pd.read_csv(file)

        
        frame["source_file"] = file.name

        frames.append(frame)

    df = pd.concat(
        frames,
        ignore_index=True
    )

    return df



def clean_dataframe(df):
    """
    Clean and validate the combined FIRMS dataframe.

    Returns:
        cleaned dataframe
        number of duplicates removed
    """

    print(f"Raw rows: {len(df)}")

  
    for column in OPTIONAL_COLUMNS:
        if column not in df.columns:
            df[column] = pd.NA

  
    missing_required = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_required:
        raise ValueError(
            f"Missing required columns: {missing_required}"
        )

 
    for column in NUMERIC_COLUMNS:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )


    df = df[
        df["latitude"].between(
            -90,
            90,
            inclusive="both"
        )
        &
        df["longitude"].between(
            -180,
            180,
            inclusive="both"
        )
    ]

   
    df = df[
        df["frp"].notna()
        &
        (df["frp"] >= 0)
    ]

  

    df = df[
        df["acq_date"].notna()
        &
        df["acq_time"].notna()
    ]

   
  
    df["acq_time"] = pd.to_numeric(
        df["acq_time"],
        errors="coerce"
    )

    df = df[
        df["acq_time"].notna()
        &
        df["acq_time"].between(
            0,
            2359
        )
    ]

    df["acq_time"] = df["acq_time"].astype(int)

 
    hours = df["acq_time"] // 100
    minutes = df["acq_time"] % 100

    

    df = df[
        minutes.between(
            0,
            59
        )
    ]

    # Recalculate after filtering
    hours = df["acq_time"] // 100
    minutes = df["acq_time"] % 100

   
    df["acquired_at"] = (
        pd.to_datetime(
            df["acq_date"],
            errors="coerce"
        )
        +
        pd.to_timedelta(
            hours,
            unit="h"
        )
        +
        pd.to_timedelta(
            minutes,
            unit="m"
        )
    )


    df = df[
        df["acquired_at"].notna()
    ]

 
    if "confidence" in df.columns:

        df["confidence"] = (
            df["confidence"]
            .astype("string")
            .str.strip()
            .str.lower()
        )

        confidence_map = {
            "l": 0.33,
            "n": 0.66,
            "h": 1.00,
        }

        df["confidence_score"] = (
            df["confidence"]
            .map(confidence_map)
        )

   
    if "satellite" in df.columns:

        df["satellite"] = (
            df["satellite"]
            .astype("string")
            .str.strip()
            .str.upper()
        )

 
    if "daynight" in df.columns:

        df["daynight"] = (
            df["daynight"]
            .astype("string")
            .str.strip()
            .str.upper()
        )


    text_columns = [
        "version",
        "instrument",
        "satellite",
        "confidence",
        "daynight",
    ]

    for column in text_columns:

        if column in df.columns:

            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
            )


    df["event_id"] = (
        df["satellite"].astype("string")
        + "_"
        + df["latitude"]
        .round(5)
        .astype("string")
        + "_"
        + df["longitude"]
        .round(5)
        .astype("string")
        + "_"
        + df["acquired_at"]
        .dt.strftime("%Y%m%d%H%M")
    )

  
    before_duplicates = len(df)

    df = df.drop_duplicates(
        subset=["event_id"],
        keep="first"
    )

    removed_duplicates = (
        before_duplicates
        -
        len(df)
    )


    df = (
        df
        .sort_values(
            "acquired_at"
        )
        .reset_index(drop=True)
    )


    print(
        f"Clean rows: {len(df)}"
    )

    print(
        f"Duplicates removed: "
        f"{removed_duplicates}"
    )

    return df, removed_duplicates



def main():


    df = load_raw_files()

  
    audit = {
        "input_rows": int(
            len(df)
        ),
        "input_columns": list(
            df.columns
        ),
    }


    cleaned, duplicate_count = (
        clean_dataframe(df)
    )


    audit["output_rows"] = int(
        len(cleaned)
    )

    audit["removed_duplicates"] = int(
        duplicate_count
    )

    audit["output_columns"] = list(
        cleaned.columns
    )


    output_csv = (
        OUTPUT_DIR
        /
        "firms_cleaned.csv"
    )

    output_parquet = (
        OUTPUT_DIR
        /
        "firms_cleaned.parquet"
    )

    report_path = (
        OUTPUT_DIR
        /
        "quality_report.json"
    )


    cleaned.to_csv(
        output_csv,
        index=False
    )

   
    cleaned.to_parquet(
        output_parquet,
        index=False
    )



    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            audit,
            file,
            indent=2,
            default=str
        )

   
    print()
    print("=" * 60)
    print("CLEANING COMPLETE")
    print("=" * 60)

    print(
        f"Input rows:       "
        f"{audit['input_rows']}"
    )

    print(
        f"Output rows:      "
        f"{audit['output_rows']}"
    )

    print(
        f"Duplicates removed: "
        f"{audit['removed_duplicates']}"
    )

    print()
    print(
        f"CSV:      {output_csv}"
    )

    print(
        f"Parquet:  {output_parquet}"
    )

    print(
        f"Report:   {report_path}"
    )

    print("=" * 60)




if __name__ == "__main__":
    main()
