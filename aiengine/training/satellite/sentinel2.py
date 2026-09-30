from datetime import datetime, timedelta

import requests


STAC_URL = (
    "https://stac.dataspace.copernicus.eu/v1/search"
)


def build_datetime_range(
    acquisition_time,
    hours_before=48,
    hours_after=48,
):

    start = (
        acquisition_time
        - timedelta(
            hours=hours_before
        )
    )

    end = (
        acquisition_time
        + timedelta(
            hours=hours_after
        )
    )

    return (
        start.isoformat()
        + "Z/"
        + end.isoformat()
        + "Z"
    )


def search_sentinel2(
    latitude,
    longitude,
    acquisition_time,
    cloud_cover=40,
    limit=10,
):

    delta = 0.02

    bbox = [
        longitude - delta,
        latitude - delta,
        longitude + delta,
        latitude + delta,
    ]

    datetime_range = (
        build_datetime_range(
            acquisition_time
        )
    )

    payload = {
        "collections": [
            "sentinel-2-l2a"
        ],
        "bbox": bbox,
        "datetime": datetime_range,
        "limit": limit,
        "query": {
            "eo:cloud_cover": {
                "lt": cloud_cover
            }
        },
    }

    response = requests.post(
        STAC_URL,
        json=payload,
        timeout=120
    )

    response.raise_for_status()

    return response.json()
def choose_best_scene(
    response,
    acquisition_time
):

    features = response.get(
        "features",
        []
    )

    if not features:
        return None

    candidates = []

    for feature in features:

        properties = feature.get(
            "properties",
            {}
        )

        cloud_cover = float(
            properties.get(
                "eo:cloud_cover",
                100
            )
            or 100
        )

        item_datetime = (
            properties.get(
                "datetime"
            )
        )

        if not item_datetime:

            continue

        item_time = datetime.fromisoformat(
            item_datetime.replace(
                "Z",
                "+00:00"
            )
        )

        if (
            acquisition_time.tzinfo
            is None
        ):

            acquisition_time = (
                acquisition_time.replace(
                    tzinfo=item_time.tzinfo
                )
            )

        time_difference = abs(
            (
                item_time
                - acquisition_time
            ).total_seconds()
        ) / 3600.0

        temporal_score = max(
            0.0,
            1.0
            - min(
                time_difference / 72.0,
                1.0
            )
        )

        cloud_score = max(
            0.0,
            1.0
            - cloud_cover / 100.0
        )

        score = (
            cloud_score * 0.6
            + temporal_score * 0.4
        )

        candidates.append(
            {
                "feature": feature,
                "score": score,
                "cloud_cover":
                    cloud_cover,
                "time_difference_hours":
                    time_difference,
            }
        )

    if not candidates:
        return None

    candidates.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return candidates[0]