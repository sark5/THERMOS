def temporal_difference_hours(
    time_a,
    time_b
):
    """
    Absolute time difference in hours.
    """

    difference = (
        time_a - time_b
    )

    return abs(
        difference.total_seconds()
    ) / 3600.0