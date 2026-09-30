import pandas as pd


def remove_source_overlap(
    train,
    evaluation,
    source_column="source_id"
):

    if source_column not in train.columns:
        return evaluation.copy()

    if source_column not in evaluation.columns:
        return evaluation.copy()

    train_sources = set(
        train[
            source_column
        ]
        .dropna()
        .astype(str)
    )

    mask = ~evaluation[
        source_column
    ].astype(str).isin(
        train_sources
    )

    return evaluation[
        mask
    ].copy()