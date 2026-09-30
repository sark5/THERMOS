import os

import psycopg2
from dotenv import load_dotenv


load_dotenv(
    r"..\data-pipeline\.env"
)


connection = psycopg2.connect(
    host=os.getenv(
        "DATABASE_HOST",
        "localhost"
    ),
    port=int(
        os.getenv(
            "DATABASE_PORT",
            "5432"
        )
    ),
    dbname=os.getenv(
        "DATABASE_NAME",
        "thermos"
    ),
    user=os.getenv(
        "DATABASE_USER",
        "postgres"
    ),
    password=os.getenv(
        "DATABASE_PASSWORD"
    )
)


cursor = connection.cursor()

cursor.execute(
    """
    SELECT
        column_name,
        data_type
    FROM information_schema.columns
    WHERE table_schema = 'thermos'
      AND table_name = 'facilities'
    ORDER BY ordinal_position;
    """
)


rows = cursor.fetchall()


print()
print("=" * 60)
print("THERMOS.FACILITIES COLUMNS")
print("=" * 60)

for column_name, data_type in rows:
    print(
        f"{column_name}: {data_type}"
    )


cursor.close()
connection.close()
