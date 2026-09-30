from pathlib import Path
import os

from dotenv import load_dotenv

from app.firms.archive_client import (
    FIRMSArchiveClient
)


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parents[2]
)

OUTPUT_DIR = (
    BASE_DIR
    / "ai-engine"
    / "training"
    / "datasets"
    / "raw"
)


def main():

    env_path = (
        BASE_DIR
        / "data-pipeline"
        / ".env"
    )

    load_dotenv(
        env_path
    )

    api_key = os.getenv(
        "FIRMS_API_KEY"
    )

    if not api_key:

        raise RuntimeError(
            "FIRMS_API_KEY is missing."
        )

    area = os.getenv(
        "FIRMS_AREA",
        "IND"
    )

    start_date = os.getenv(
        "FIRMS_START_DATE"
    )

    end_date = os.getenv(
        "FIRMS_END_DATE"
    )

    if not start_date or not end_date:

        raise RuntimeError(
            "FIRMS_START_DATE and "
            "FIRMS_END_DATE are required."
        )

    sources = [
        value.strip()
        for value in os.getenv(
            "FIRMS_SOURCES",
            "VIIRS_NOAA20_SP,VIIRS_NOAA21_SP"
        ).split(",")
        if value.strip()
    ]

    client = FIRMSArchiveClient(
        api_key
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    for source in sources:

        print()
        print(
            "=" * 70
        )

        print(
            f"Downloading {source}"
        )

        print(
            "=" * 70
        )

        frame = client.download_range(
            source=source,
            area=area,
            start_date=start_date,
            end_date=end_date,
        )

        source_folder = (
            OUTPUT_DIR
            / source.lower()
        )

        source_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        output = (
            source_folder
            / "firms_raw.csv"
        )

        frame.to_csv(
            output,
            index=False
        )

        print()
        print(
            f"Saved: {output}"
        )

        print(
            f"Records: {len(frame)}"
        )


if __name__ == "__main__":
    main()