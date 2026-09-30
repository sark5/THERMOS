
def parse_osm_response(data: dict):

    facilities = []

    elements = data.get(
        "elements",
        []
    )

    for element in elements:

        tags = element.get(
            "tags",
            {}
        )

        # PostgreSQL osm_id is BIGINT,
        # so store only the numeric OSM ID.
        osm_id = element.get("id")

        name = tags.get(
            "name"
        )

        raw_type = (
            tags.get("industrial")
            or tags.get("man_made")
            or tags.get("power")
            or tags.get("resource")
            or tags.get("landuse")
            or "industrial"
        ).lower()

        if "refinery" in raw_type or "petroleum" in raw_type or tags.get("industrial") == "refinery":
            facility_type = "refinery"
        elif "flare" in raw_type or tags.get("man_made") == "flare":
            facility_type = "flare"
        elif "power" in raw_type or tags.get("power") == "plant":
            facility_type = "powerplant"
        elif "mine" in raw_type or "mining" in raw_type or tags.get("resource") == "mining":
            facility_type = "mine"
        elif "quarry" in raw_type or tags.get("landuse") == "quarry":
            facility_type = "quarry"
        elif "chemical" in raw_type or tags.get("industrial") == "chemical":
            facility_type = "chemical"
        else:
            facility_type = "industrial"

        latitude = None
        longitude = None

        if "lat" in element:
            latitude = element["lat"]
            longitude = element["lon"]

        elif "center" in element:
            latitude = element["center"].get("lat")
            longitude = element["center"].get("lon")

        if latitude is None or longitude is None:
            continue

        facilities.append({
            "osm_id": osm_id,
            "name": name,
            "facility_type": facility_type,
            "operator": tags.get("operator"),
            "latitude": latitude,
            "longitude": longitude,
            "tags": tags
        })

    return facilities
