import psycopg2
from app.config import DATABASE_CONFIG

def get_connection():
    connection=psycopg2.connect(
        **DATABASE_CONFIG
    )
    return connection