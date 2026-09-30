import os
from dotenv import load_dotenv
load_dotenv()
FIRMS_API_KEY=os.getenv(
    "FIRMS_API_KEY"
)
DATABASE_CONFIG={
    "host":os.getenv(
        "DATABASE_HOST",
        "localhost"
    ),
    "port":int(
        os.getenv(
            "DATABASE_PORT",
            "5432"
        )
    ),
    "database":os.getenv(
        "DATABASE_NAME",
        "thermos"
    ),
    "user":os.getenv(
        "DATABASE_USER",
        "postgres"
    ),
    "password":os.getenv(
        "DATABASE_PASSWORD"
    )
}
FIRMS_BASE_URL=(
    "https://firms.modaps.eosdis.nasa.gov/api"
)
if not FIRMS_API_KEY:
    raise ValueError(
        "FIRMS_API_KEY is missing from .env"
    )