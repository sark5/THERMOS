import pandas as pd
from app.database.postgres import get_connection


def clean_value(value):
    """
    Convert NaN/NaT values into None so PostgreSQL
    can store them as NULL.
    """

    if value is None:
        return None

    try:
        if value != value:
            return None
    except Exception:
        pass

    return value


def insert_events(df):

    connection = get_connection()
    cursor = connection.cursor()

    inserted = 0
    skipped = 0
    errors = 0

    sql = """
        INSERT INTO thermos.thermal_events
        (
            event_id,
            source,
            satellite,
            latitude,
            longitude,
            location,
            acquired_at,
            brightness,
            bright_t31,
            frp,
            confidence,
            day_night,
            scan,
            track
        )
        VALUES
        (
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
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        ON CONFLICT (event_id)
        DO NOTHING
    """

    for _, row in df.iterrows():

        try:

            parameters = (
                # event_id
                clean_value(
                    row.get("event_id")
                ),

                # source
                "NASA_FIRMS",

                # satellite
                clean_value(
                    row.get("satellite")
                ),

                # latitude
                clean_value(
                    row.get("latitude")
                ),

                # longitude
                clean_value(
                    row.get("longitude")
                ),

                # ST_MakePoint longitude
                clean_value(
                    row.get("longitude")
                ),

                # ST_MakePoint latitude
                clean_value(
                    row.get("latitude")
                ),

                # acquired_at
                clean_value(
                    row.get("acquired_at")
                ),

                # brightness
                clean_value(
                    row.get("bright_ti4")
                ),

                # bright_t31
                clean_value(
                    row.get("bright_ti5")
                ),

                # FRP
                clean_value(
                    row.get("frp")
                ),

                # confidence
                clean_value(
                    row.get("confidence")
                    if pd.notna(row.get("confidence"))
                    else None
                ),

                # day/night
                clean_value(
                    row.get("daynight")
                ),

                # scan
                clean_value(
                    row.get("scan")
                ),

                # track
                clean_value(
                    row.get("track")
                )
            )

            cursor.execute(
                sql,
                parameters
            )

            if cursor.rowcount == 1:
                inserted += 1
            else:
                skipped += 1

        except Exception as error:

            errors += 1

            print(
                f"Insert error for "
                f"{row.get('event_id')}: {error}"
            )

            connection.rollback()

            # Recreate cursor after rollback
            cursor.close()
            cursor = connection.cursor()

    connection.commit()

    cursor.close()
    connection.close()

    return inserted, skipped, errors
