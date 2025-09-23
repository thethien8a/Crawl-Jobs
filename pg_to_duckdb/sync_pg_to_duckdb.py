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


def incremental_by_timestamp(
    con: duckdb.DuckDBPyConnection,
    schema_name: str,
    table: str,
    pg_conn: str,
    cursor_column: str,

) -> None:

    # Ensure target table exists with the desired schema (including computed cols)
    con.execute(
        f"""
            CREATE TABLE IF NOT EXISTS {schema_name}.{table} AS
            SELECT *
            FROM postgres_scan('{pg_conn}', 'public', '{table}')
            WHERE 1=0
        """
        
    )

    if con.execute(f"SELECT COUNT(*) FROM {schema_name}.{table} WHERE DATE({cursor_column}) = CURRENT_DATE").fetchone()[0] == 0:
        con.execute(f"INSERT INTO {schema_name}.{table} SELECT * FROM postgres_scan('{pg_conn}', 'public', '{table}') WHERE DATE({cursor_column}) = CURRENT_DATE")
    else:
        con.execute(
            f"""
                WITH max_cursor AS (
                    SELECT 
                        *
                    FROM
                        postgres_scan('{pg_conn}', 'public', '{table}')
                    WHERE
                        DATE({cursor_column}) = CURRENT_DATE
                )
                MERGE INTO {schema_name}.{table}
                USING max_cursor
                ON {schema_name}.{table}.job_title = max_cursor.job_title 
                    AND {schema_name}.{table}.company_name = max_cursor.company_name 
                    AND {schema_name}.{table}.source_site = max_cursor.source_site
                WHEN MATCHED THEN
                    UPDATE SET
                        {schema_name}.{table}.* = max_cursor.*
                WHEN NOT MATCHED THEN
                    INSERT VALUES (max_cursor.*)
            """
        )
        
            

def main() -> int:
    # Cấu hình DuckDB
    duckdb_path = os.getenv("DUCKDB_PATH")
    schema_name = "staging"
    table = "jobs"
    cursor_column = "scraped_at"

    pg_conn = build_pg_conn_string()

    con = duckdb.connect(duckdb_path)
    ensure_duckdb(con, schema_name)

    incremental_by_timestamp(con, schema_name, table, pg_conn, cursor_column)
    print(
        f"Incremental sync completed: {schema_name}.{table} using cursor '{cursor_column}'"
    )

    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
