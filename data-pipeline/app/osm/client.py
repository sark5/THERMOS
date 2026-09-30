import time
import requests


class OSMClient:
    OVERPASS_URLS = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://overpass.private.coffee/api/interpreter",
    ]

    def query(
        self,
        south: float,
        west: float,
        north: float,
        east: float
    ):
        query = f"""
        [out:json][timeout:180];

        (
            nwr["industrial"]({south},{west},{north},{east});
            nwr["landuse"="industrial"]({south},{west},{north},{east});
            nwr["landuse"="quarry"]({south},{west},{north},{east});
            nwr["resource"="mining"]({south},{west},{north},{east});
            nwr["power"="plant"]({south},{west},{north},{east});
            nwr["man_made"="works"]({south},{west},{north},{east});
            nwr["man_made"="petroleum_refinery"]({south},{west},{north},{east});
            nwr["man_made"="flare"]({south},{west},{north},{east});
            nwr["industrial"="refinery"]({south},{west},{north},{east});
            nwr["industrial"="chemical"]({south},{west},{north},{east});
            nwr["industrial"="factory"]({south},{west},{north},{east});
            nwr["industrial"="mine"]({south},{west},{north},{east});
        );

        out center tags;
        """

        headers = {
            "User-Agent": "THERMOS/1.0 (OSM data pipeline)",
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        last_error = None

        for url in self.OVERPASS_URLS:
            for attempt in range(3):
                try:
                    print(
                        f"Requesting OSM data..."
                        f"\nServer: {url}"
                        f"\nAttempt: {attempt + 1}/3"
                    )

                    response = requests.post(
                        url,
                        data={"data": query},
                        headers=headers,
                        timeout=180,
                    )

                    response.raise_for_status()

                    print("OSM request successful.")
                    return response.json()

                except requests.RequestException as e:
                    last_error = e

                    print(
                        f"OSM request failed: {e}"
                    )

                    if attempt < 2:
                        print("Retrying in 5 seconds...")
                        time.sleep(5)

            print(f"Switching Overpass server...")

        raise RuntimeError(
            f"All Overpass servers failed. "
            f"Last error: {last_error}"
        )
