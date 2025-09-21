import os
import sys

import duckdb
from dotenv import load_dotenv

load_dotenv()

def build_pg_conn_string() -> str:
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB")
    user = os.getenv("POSTGRES_USER")
    pwd = os.getenv("POSTGRES_PASSWORD")
    return f"host={host} dbname={db} user={user} password={pwd} port={port}"


def ensure_duckdb(con: duckdb.DuckDBPyConnection, schema_name: str) -> None:
    con.execute("INSTALL postgres_scanner; LOAD postgres_scanner;")
    con.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name};")


def full_refresh(con: duckdb.DuckDBPyConnection, schema_name: str, table: str, pg_conn: str) -> None:
    con.execute(
        f"""
        CREATE OR REPLACE TABLE {schema_name}.{table} AS
        SELECT * FROM postgres_scan('{pg_conn}', 'public', '{table}')
        """
    )


def incremental_by_timestamp(
    con: duckdb.DuckDBPyConnection,
    schema_name: str,
    table: str,
    pg_conn: str,
    cursor_column: str,
) -> None:
    # Create table if not exists to support first run
    con.execute(
        f"CREATE TABLE IF NOT EXISTS {schema_name}.{table} AS SELECT * FROM postgres_scan('{pg_conn}', 'public', '{table}') WHERE 1=0"
    )
    # Insert only rows newer than current max(cursor_column)
    con.execute(
        f"""
        INSERT INTO {schema_name}.{table}
        SELECT *
        FROM postgres_scan('{pg_conn}', 'public', '{table}')
        WHERE {cursor_column} > (SELECT COALESCE(MAX({cursor_column}), TIMESTAMP '1970-01-01') FROM {schema_name}.{table})
        """
    )


def main() -> int:
    # Cấu hình DuckDB
    duckdb_path = os.getenv("DUCKDB_PATH")
    schema_name = "raw"
    table = "jobs"
    cursor_column = "scraped_at"
    
    # Chỉ có 2 mode: full và incremental
    mode = "incremental"

    pg_conn = build_pg_conn_string()

    con = duckdb.connect(duckdb_path)
    ensure_duckdb(con, schema_name)

    if mode == "full":
        full_refresh(con, schema_name, table, pg_conn)
        print(f"Full refresh completed: {schema_name}.{table}")
    else:
        incremental_by_timestamp(con, schema_name, table, pg_conn, cursor_column)
        print(
            f"Incremental sync completed: {schema_name}.{table} using cursor '{cursor_column}'"
        )

    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
