import os
import sys
from typing import Optional

import duckdb
from dotenv import load_dotenv

load_dotenv()

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


def incremental_by_timestamp(
    con: duckdb.DuckDBPyConnection,
    schema_name: str,
    table: str,
    pg_conn: str,
    cursor_column: str,
) -> None:
    # Define source CTE for today's data
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE src AS
        SELECT
            job_url,
            job_title,
            company_name,
            salary,
            location,
            job_type,
            job_industry,
            experience_level,
            education_level,
            job_position,
            job_description,
            requirements,
            benefits,
            job_deadline,
            source_site,
            search_keyword,
            {cursor_column} AS scraped_at,
            DATE({cursor_column}) AS scraped_date
        FROM postgres_scan('{pg_conn}', 'public', '{table}')
        WHERE DATE({cursor_column}) = CURRENT_DATE
    """)

    # Create target table if not exists, inferring schema from source
    con.execute(f"""
        CREATE TABLE IF NOT EXISTS {schema_name}.{table} AS
        SELECT * FROM src WHERE 1=0
    """)

    # Daily upsert by key (job_url, scraped_date)
    con.execute(
        f"""
        MERGE INTO {schema_name}.{table} AS t
        USING src AS s
        ON t.job_title = s.job_title  
           AND t.company_name = s.company_name 
           AND t.source_site = s.source_site
           AND t.scraped_date = s.scraped_date
        WHEN MATCHED THEN UPDATE SET
            job_title        = s.job_title,
            company_name     = s.company_name,
            salary           = s.salary,
            location         = s.location,
            job_type         = s.job_type,
            job_industry     = s.job_industry,
            experience_level = s.experience_level,
            education_level  = s.education_level,
            job_position     = s.job_position,
            job_description  = s.job_description,
            requirements     = s.requirements,
            benefits         = s.benefits,
            job_deadline     = s.job_deadline,
            source_site      = s.source_site,
            search_keyword   = s.search_keyword,
            scraped_at       = s.scraped_at
        WHEN NOT MATCHED THEN INSERT (
            job_url, job_title, company_name, salary, location, job_type, job_industry,
            experience_level, education_level, job_position, job_description,
            requirements, benefits, job_deadline, source_site, search_keyword,
            scraped_at, scraped_date
        ) VALUES (
            s.job_url, s.job_title, s.company_name, s.salary, s.location, s.job_type, s.job_industry,
            s.experience_level, s.education_level, s.job_position, s.job_description,
            s.requirements, s.benefits, s.job_deadline, s.source_site, s.search_keyword,
            s.scraped_at, s.scraped_date
        )
    """)


def main() -> int:
    
    # Cấu hình DuckDB
    duckdb_path = os.getenv("DUCKDB_PATH")
    schema_name = "bronze"
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
