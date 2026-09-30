def normalize_firms_type(value):

    if value is None:
        return None

    try:

        value = int(float(value))

    except (
        ValueError,
        TypeError
    ):

        return None

    if value in [0, 1, 2, 3]:

        return value

    return None