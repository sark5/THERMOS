import requests

from app.config import (
    FIRMS_API_KEY,
    FIRMS_BASE_URL
)


class FIRMSClient:

    def __init__(self):

        if not FIRMS_API_KEY:
            raise RuntimeError(
                "FIRMS_API_KEY is missing from .env"
            )

        self.api_key = FIRMS_API_KEY
        self.base_url = FIRMS_BASE_URL

    def check_api_key(self):

        url = (
            f"{self.base_url}/data_availability/csv/"
            f"{self.api_key}/VIIRS_NOAA21_NRT"
        )

        print()
        print("Checking NASA FIRMS MAP_KEY...")

        response = requests.get(
            url,
            timeout=60
        )

        print(
            f"NASA response: HTTP {response.status_code}"
        )

        if response.status_code == 401:
            raise RuntimeError(
                "NASA FIRMS rejected the MAP_KEY."
            )

        response.raise_for_status()

        print(
            "NASA FIRMS MAP_KEY: VALID"
        )

        return True

    def get_area_data(
        self,
        source: str,
        area: str,
        days: int = 1
    ):

        self.check_api_key()

        url = (
            f"{self.base_url}/area/csv/"
            f"{self.api_key}/"
            f"{source}/"
            f"{area}/"
            f"{days}"
        )

        print()
        print("================================")
        print("NASA FIRMS REQUEST")
        print("================================")

        print(f"Source : {source}")
        print(f"Area   : {area}")
        print(f"Days   : {days}")

        print()
        print("Requesting data...")

        response = requests.get(
            url,
            timeout=120
        )

        if response.status_code != 200:

            print()
            print("NASA FIRMS ERROR")
            print("----------------")

            print(
                f"HTTP status: "
                f"{response.status_code}"
            )

            print()
            print(
                response.text[:1000]
            )

            response.raise_for_status()

        print()
        print(
            f"Downloaded "
            f"{len(response.content)} bytes"
        )

        return response.text