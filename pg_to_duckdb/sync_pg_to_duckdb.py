import os
import sys
from typing import Optional

import duckdb
from dotenv import load_dotenv


def get_env(name: str, default: Optional[str] = None) -> str:
    value = os.getenv(name, default)
    if value is None or value == "":
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def build_pg_conn_string() -> str:
    host = get_env("POSTGRES_HOST")
    port = get_env("POSTGRES_PORT", "5432")
    db = get_env("POSTGRES_DB")
    user = get_env("POSTGRES_USER")
    pwd = get_env("POSTGRES_PASSWORD")
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
    # Load .env from project root if present
    load_dotenv()

    duckdb_path = get_env("DUCKDB_PATH")
    schema_name = os.getenv("DUCKDB_SCHEMA", "raw")
    # Which table and cursor to sync (defaults match project conventions)
    table = os.getenv("PG_TABLE", "jobs")
    cursor_column = os.getenv("PG_CURSOR_COLUMN", "scraped_at")

    mode = (os.getenv("SYNC_MODE", "incremental").lower()).strip()
    if mode not in {"full", "incremental"}:
        print("SYNC_MODE must be 'full' or 'incremental'", file=sys.stderr)
        return 2

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
