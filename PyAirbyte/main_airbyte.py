import os

import airbyte as ab
from dotenv import load_dotenv

load_dotenv()

src = ab.get_source(
    name="source-postgres",
    config={
        "host": os.getenv("POSTGRES_HOST"),
        "port": os.getenv("POSTGRES_PORT"),
        "database": os.getenv("POSTGRES_DB"),
        "username": os.getenv("POSTGRES_USER"),
        "password": os.getenv("POSTGRES_PASSWORD"),
    },
)

dst = ab.get_destination(
    "destination-duckdb", config={"destination_path": os.getenv("DUCKDB_PATH")}
)

conn = ab.get_connection(source=src, destination=dst, streams="*")
conn.sync()
