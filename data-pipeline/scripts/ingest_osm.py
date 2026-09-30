from app.osm.client import OSMClient
from app.osm.parser import parse_osm_response
from app.osm.ingestion import insert_facilities


def main():
    print("   Thermos osm Ingestion   ")

    south = 20.20
    west = 85.75
    north = 20.40
    east = 85.90

    client = OSMClient()

    print("Requesting OSM Data.....")

    data = client.query(
        south,
        west,
        north,
        east
    )

    facilities = parse_osm_response(data)

    print(f"Facilities found: {len(facilities)}")

    inserted, skipped = insert_facilities(facilities)

    print("Ingestion done...")
    print(f"Processed: {len(facilities)}")
    print(f"Inserted: {inserted}")
    print(f"Skipped: {skipped}")


if __name__ == "__main__":
    main()
