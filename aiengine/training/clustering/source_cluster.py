from datetime import datetime

from clustering.distance import (
    haversine_distance
)

from clustering.temporal import (
    temporal_difference_hours
)


DEFAULT_DISTANCE_METERS = 1000

DEFAULT_TIME_HOURS = 48


class ThermalSourceClusterer:

    def __init__(
        self,
        distance_meters=DEFAULT_DISTANCE_METERS,
        time_hours=DEFAULT_TIME_HOURS,
    ):

        self.distance_meters = (
            distance_meters
        )

        self.time_hours = (
            time_hours
        )

    def _compatible(
        self,
        event,
        representative,
    ):

        distance = haversine_distance(
            event["latitude"],
            event["longitude"],
            representative["latitude"],
            representative["longitude"],
        )

        time_difference = (
            temporal_difference_hours(
                event["acquired_at"],
                representative["acquired_at"]
            )
        )

        return (
            distance
            <= self.distance_meters
            and
            time_difference
            <= self.time_hours
        )

    def cluster(
        self,
        events
    ):

        if not events:
            return []

        events = sorted(
            events,
            key=lambda event:
                event["acquired_at"]
        )

        clusters = []

        for event in events:

            assigned = False

            for cluster in clusters:

                representative = (
                    cluster[0]
                )

                if self._compatible(
                    event,
                    representative
                ):

                    cluster.append(
                        event
                    )

                    assigned = True

                    break

            if not assigned:

                clusters.append(
                    [event]
                )

        return clusters