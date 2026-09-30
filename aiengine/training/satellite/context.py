def derive_context_scores(
    worldcover_features
):

    tree_fraction = float(
        worldcover_features.get(
            "tree_fraction",
            0.0
        )
    )

    cropland_fraction = float(
        worldcover_features.get(
            "cropland_fraction",
            0.0
        )
    )

    builtup_fraction = float(
        worldcover_features.get(
            "builtup_fraction",
            0.0
        )
    )

    return {
        "forest_context": round(
            tree_fraction,
            4
        ),

        "agricultural_context": round(
            cropland_fraction,
            4
        ),

        "builtup_context": round(
            builtup_fraction,
            4
        ),
    }