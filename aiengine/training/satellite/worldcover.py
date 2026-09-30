import numpy as np
import rasterio
from rasterio.windows import from_bounds
WORLDCOVER_CLASSES = {
    10: "TREE_COVER",
    20: "SHRUBLAND",
    30: "GRASSLAND",
    40: "CROPLAND",
    50: "BUILT_UP",
    60: "BARE_SPARSE",
    70: "SNOW_ICE",
    80: "PERMANENT_WATER",
    90: "HERBACEOUS_WETLAND",
    95: "MANGROVE",
    100: "MOSS_LICHEN",
}


INDUSTRIAL_RELATED_CLASSES = {
    50: "BUILT_UP",
}


VEGETATION_CLASSES = {
    10: "TREE_COVER",
    20: "SHRUBLAND",
    30: "GRASSLAND",
    95: "MANGROVE",
    100: "MOSS_LICHEN",
}


AGRICULTURE_CLASSES = {
    40: "CROPLAND",
}


def class_name(class_value):

    try:
        value = int(class_value)
    except (
        ValueError,
        TypeError,
    ):
        return "UNKNOWN"

    return WORLDCOVER_CLASSES.get(
        value,
        "UNKNOWN"
    )


def read_worldcover_window(
    raster_path,
    longitude,
    latitude,
    radius_degrees=0.0025,
):

    with rasterio.open(
        raster_path
    ) as dataset:

        left = (
            longitude
            - radius_degrees
        )

        right = (
            longitude
            + radius_degrees
        )

        bottom = (
            latitude
            - radius_degrees
        )

        top = (
            latitude
            + radius_degrees
        )

        window = from_bounds(
            left,
            bottom,
            right,
            top,
            transform=dataset.transform
        )

        data = dataset.read(
            1,
            window=window
        )

        transform = (
            dataset.window_transform(
                window
            )
        )

    return data, transform


def calculate_landcover_statistics(
    data
):

    values = data[
        data > 0
    ]

    if values.size == 0:

        return {
            "landcover_class": None,
            "landcover_class_name":
                "UNKNOWN",
            "tree_fraction": 0.0,
            "cropland_fraction": 0.0,
            "builtup_fraction": 0.0,
            "vegetation_fraction": 0.0,
            "class_distribution": {},
        }

    unique, counts = np.unique(
        values,
        return_counts=True
    )

    total = int(
        counts.sum()
    )

    distribution = {}

    for class_value, count in zip(
        unique,
        counts
    ):

        distribution[
            str(int(class_value))
        ] = round(
            int(count)
            / total,
            4
        )

    dominant_index = int(
        np.argmax(counts)
    )

    dominant_class = int(
        unique[dominant_index]
    )

    tree_fraction = sum(
        distribution.get(
            str(class_value),
            0.0
        )
        for class_value in [
            10,
            20,
            30,
            95,
            100,
        ]
    )

    cropland_fraction = (
        distribution.get(
            "40",
            0.0
        )
    )

    builtup_fraction = (
        distribution.get(
            "50",
            0.0
        )
    )

    return {
        "landcover_class":
            dominant_class,
        "landcover_class_name":
            class_name(
                dominant_class
            ),
        "tree_fraction":
            round(tree_fraction, 4),
        "cropland_fraction":
            round(cropland_fraction, 4),
        "builtup_fraction":
            round(builtup_fraction, 4),
        "vegetation_fraction":
            round(tree_fraction, 4),
        "class_distribution":
            distribution,
    }