import hashlib


def generate_source_id(
    cluster
):
    """
    Generate deterministic source ID based
    on the earliest observation.
    """

    if not cluster:
        raise ValueError(
            "Cluster is empty."
        )

    first = min(
        cluster,
        key=lambda event:
            event["acquired_at"]
    )

    raw = (
        f"{round(first['latitude'], 4)}|"
        f"{round(first['longitude'], 4)}|"
        f"{first['acquired_at'].date()}"
    )

    digest = hashlib.sha1(
        raw.encode("utf-8")
    ).hexdigest()[:12]

    return (
        f"THERMAL_SOURCE_{digest.upper()}"
    )