**OPERATIONS (UPDATED: DuckDB postgres_scanner Implementation)**

**Run Order (Airflow):**
1. run_spiders
2. soda_scan_check1
3. soda_scan_check2
4. soda_scan_check3
5. duckdb_sync (pg_to_duckdb/sync_pg_to_duckdb.py)
6. dbt_run
7. dbt_test

**DuckDB Sync (local execution):**
- Incremental by day (upsert): `python pg_to_duckdb/sync_pg_to_duckdb.py`
- With specific date: `set SYNC_DATE=YYYY-MM-DD & python pg_to_duckdb/sync_pg_to_duckdb.py`

**Env vars:**
- DUCKDB_PATH: path to .duckdb file
- DUCKDB_SCHEMA: schema in DuckDB (default: staging)
- PG_TABLE: source table in Postgres (default: jobs)
- PG_CURSOR_COLUMN: timestamp column (default: scraped_at)
- POSTGRES_HOST/PORT/DB/USER/PASSWORD
- SYNC_DATE (optional, YYYY-MM-DD)

**Notes:**
- No Airbyte/PyAirbyte required.
- Single-writer discipline for DuckDB.
- Parameterize Airflow `duckdb_sync` via env if needed.
- `test_connect.py` in DuckDB/test for query testing.