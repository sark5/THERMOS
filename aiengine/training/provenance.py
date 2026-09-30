from datetime import datetime


PIPELINE_VERSION = "7.0.0"


def add_provenance(
    df,
    source_name
):

    df = df.copy()

    df[
        "dataset_source"
    ] = source_name

    df[
        "pipeline_version"
    ] = PIPELINE_VERSION

    df[
        "ingested_at"
    ] = datetime.utcnow()

    return df