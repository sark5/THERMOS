import pandas as pd


REQUIRED_COLUMNS = [
    "latitude",
    "longitude",
    "acq_date",
    "acq_time"
]


def validate_required_columns(
    df: pd.DataFrame
):
    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Missing FIRMS columns: "
            + ", ".join(missing)
        )


def validate_coordinates(
    df: pd.DataFrame
) -> pd.DataFrame:

    df = df.copy()

    df["latitude"] = pd.to_numeric(
        df["latitude"],
        errors="coerce"
    )

    df["longitude"] = pd.to_numeric(
        df["longitude"],
        errors="coerce"
    )

    df = df.dropna(
        subset=[
            "latitude",
            "longitude"
        ]
    )

    df = df[
        df["latitude"].between(-90, 90)
    ]

    df = df[
        df["longitude"].between(-180, 180)
    ]

    return df


def clean_numeric_column(
    df: pd.DataFrame,
    column: str
) -> pd.DataFrame:

    df = df.copy()

    if column in df.columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df


def validate_numeric_fields(
    df: pd.DataFrame
) -> pd.DataFrame:

    df = df.copy()

    numeric_columns = [
        "frp",
        "scan",
        "track",
        "bright_ti4",
        "bright_ti5",
        "bright_t31"
    ]

    for column in numeric_columns:

        df = clean_numeric_column(
            df,
            column
        )

    return df


def normalize_confidence(
    df: pd.DataFrame
) -> pd.DataFrame:

    df = df.copy()

    if "confidence" not in df.columns:
        return df

    # FIRMS confidence can be numeric
    # or categorical depending on product.

    original = df["confidence"]

    numeric = pd.to_numeric(
        original,
        errors="coerce"
    )

    df["confidence"] = numeric

    # Preserve categorical confidence
    # information in metadata later.

    categorical_mask = (
        numeric.isna()
        & original.notna()
    )

    df["confidence_category"] = None

    df.loc[
        categorical_mask,
        "confidence_category"
    ] = (
        original[
            categorical_mask
        ]
        .astype(str)
        .str.lower()
    )

    return df


def validate_frp(
    df: pd.DataFrame
) -> pd.DataFrame:

    df = df.copy()

    if "frp" in df.columns:

        df["frp"] = pd.to_numeric(
            df["frp"],
            errors="coerce"
        )

        df = df[
            (df["frp"].isna())
            |
            (df["frp"] >= 0)
        ]

    return df