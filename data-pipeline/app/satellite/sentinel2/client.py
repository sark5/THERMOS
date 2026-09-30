import requests
class Sentinel2Client:
    def __init__(self):
        self.base_url=base_url or (
          "https://catalogue.dataspace.copernicus.eu/odata/v1.0"
        )
    def search(
            self,
            latitude,
            longitude,
            start_date,
            end_date,
            max_cloud_cover=30
    ):
        point=(
            f"POINT({longitude} {latitude})"
        )
        filter_query=(
            f"Collection/Name eq "
            f"'SENTINEL-2' "
            f"and OData.CSC.Intersects("
            f"Footprint, geography'{point}') "
            f"and ContentDate/Start ge "
            f"{start_date}T00:00:00.000Z "
            f"and ContentDate/Start le "
            f"{end_date}T23:59:59.999Z"
        )
        params={
            "$filter": filter_query,
            "$orderby": "ContentDate/Start desc",
            "$top": 10
        }
        response=requests.get(
            f"{self.base_url}/Products",
            params=params,
            timeout=60
        )
        response.raise_for_status()
        return response.json()