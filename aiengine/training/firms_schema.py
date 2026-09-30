REQUIRED_COLUMNS=[
    "latitude",
    "longitude",
    "acq_date",
    "acq_time",
    "satellite",
    "instrument",
    "confidence",
    "version",
    "frp",
    "daynight"
]
OPTIONAL_COLUMNS=[
    "bright_ti4",
    "bright_ti5",
    "scan",
    "track",
    "type"
]
NUMERIC_COLUMNS=[
    "latitude",
    "longitude",
    "bright_ti4",
    "bright_ti5",
    "scan",
    "track",
    "frp"
]
TEXT_COLUMNS=[
    "satellite",
    "instrument",
    "confidence",
    "version",
    "daynight"
]
def validate_schema(columns):
    solumns=set(columns)
    missing=[
        column
        for column  in  REQUIRED_COLUMNS
        if column not in columns
    ]
    if missing:
        raise ValueError(
            f"Missing required FIRMS columns: {missing}"
            + ", ".join(missing)
        )
    return {
        "valid":True,
        "missing_optional":[
            column
            for column in OPTIONAL_COLUMNS
            if column not in columns
        ],
    }