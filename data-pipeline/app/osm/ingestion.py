from app.database.postgres import get_connection
def insert_facilities( facilities ):
    connection=get_connection()
    cursor=connection.cursor()
    inserted=0
    skipped=0
    sql="""
       INSERT INTO thermos.facilities (
       osm_id,
       name,
       facility_type,
       operator,
       latitude,
       longitude,
       location,
       source,
       metadata
       )
       VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            ST_SetSRID(
                ST_MakePoint(
                    %s,
                    %s
                ),
                4326
            ),
            'OPENSTREETMAP',
            %s
        )
        ON CONFLICT (osm_id)
        DO UPDATE SET
            name = EXCLUDED.name,
            facility_type =
                EXCLUDED.facility_type,
            operator =
                EXCLUDED.operator,
            latitude =
                EXCLUDED.latitude,
            longitude =
                EXCLUDED.longitude,
            location =
                EXCLUDED.location,
            metadata =
                EXCLUDED.metadata,
            updated_at =
                NOW()
   """
    for facility in facilities:
        try:
            cursor.execute(
                sql,
                (
                    facility["osm_id"],
                    facility["name"],
                    facility["facility_type"],
                    facility["operator"],
                    facility["latitude"],
                    facility["longitude"],
                    facility["longitude"],
                    facility["latitude"],
                    __import__(
                        "json"
                    ).dumps(
                        facility["tags"]
                    )
                )
            )
            inserted+=1
        except Exception as error:
            print("Facility insert error:",error)
            connection.rollback()
            skipped+=1
    connection.commit()
    cursor.close()
    connection.close()
    return inserted,skipped