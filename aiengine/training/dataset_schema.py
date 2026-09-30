from typing import Final


CANONICAL_FIRMS_COLUMNS: Final[list[str]] = [
    "event_id",
    "latitude",
    "longitude",
    "acquired_at",

    "brightness",
    "bright_t31",
    "frp",

    "confidence",
    "confidence_score",

    "day_night",
    "day_night_numeric",

    "scan",
    "track",

    "firms_type",

    "training_source",
    "source_year",
    "source_file",
]


TARGET_CLASSES: Final[list[str]] = [
    "INDUSTRIAL_FLARE",
    "INDUSTRIAL_FIRE",
    "MINING",
    "AGRICULTURAL",
    "WILDFIRE",
    "UNCLASSIFIED",
]


SP_TRAINING_SOURCES: Final[list[str]] = [
    "VIIRS_NOAA20_SP",
    "VIIRS_NOAA21_SP",
]


NRT_SOURCES: Final[list[str]] = [
    "VIIRS_NOAA21_NRT",
]