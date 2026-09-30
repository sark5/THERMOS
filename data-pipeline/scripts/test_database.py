
import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).resolve().parents[1]
    )
)
from app.database.postgres import get_connection


def main():

    print()
    print("================================")
    print("DATABASE CONNECTION TEST")
    print("================================")
    print()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        "SELECT current_database(), current_user;"
    )

    database, user = cursor.fetchone()

    print(f"Database : {database}")
    print(f"User     : {user}")

    cursor.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'thermos'
            AND table_name = 'thermal_events'
        );
        """
    )

    exists = cursor.fetchone()[0]

    print(f"Table exists : {exists}")

    cursor.close()
    connection.close()

    print()

    if exists:
        print("SUCCESS: Database is ready.")
    else:
        print("ERROR: thermal_events table missing.")


if __name__ == "__main__":
    main()