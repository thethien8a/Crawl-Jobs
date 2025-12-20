import psycopg2
from dotenv import load_dotenv
import os
load_dotenv()

def connect_to_postgres():
    try:
        print("Connecting to PostgreSQL database...")
        connection = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            database=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            port=os.getenv("POSTGRES_PORT")
        )

        print("Connected to PostgreSQL database successfully")
        return connection
    except (Exception, psycopg2.Error) as error:
        print(f"Error while connecting to PostgreSQL: {error}")
        return None
