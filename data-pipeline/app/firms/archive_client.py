from datetime import date, timedelta
from io import StringIO

import pandas as pd
import requests


FIRMS_BASE_URL = (
    "https://firms.modaps.eosdis.nasa.gov/api/area/csv"
)


class FIRMSArchiveClient:

    def __init__(
        self,
        api_key: str
    ):

        self.api_key = api_key

    def download_chunk(
        self,
        source: str,
        area: str,
        start_date: date,
        days: int = 5,
    ) -> pd.DataFrame:

        url = (
            f"{FIRMS_BASE_URL}/"
            f"{self.api_key}/"
            f"{source}/"
            f"{area}/"
            f"{days}/"
            f"{start_date.isoformat()}"
        )

        response = requests.get(
            url,
            timeout=180
        )

        response.raise_for_status()

        if not response.text.strip():
            return pd.DataFrame()

        return pd.read_csv(
            StringIO(
                response.text
            )
        )

    def download_range(
        self,
        source: str,
        area: str,
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:

        start = date.fromisoformat(
            start_date
        )

        end = date.fromisoformat(
            end_date
        )

        frames = []

        current = start

        while current <= end:

            remaining_days = (
                end - current
            ).days + 1

            chunk_days = min(
                remaining_days,
                5
            )

            print(
                f"[{source}] "
                f"{current} → "
                f"{current + timedelta(days=chunk_days - 1)}"
            )

            frame = self.download_chunk(
                source=source,
                area=area,
                start_date=current,
                days=chunk_days,
            )

            if not frame.empty:

                frames.append(
                    frame
                )

                print(
                    f"    records={len(frame)}"
                )

            current += timedelta(
                days=chunk_days
            )

        if not frames:

            return pd.DataFrame()

        return pd.concat(
            frames,
            ignore_index=True
        )