**OPERATIONS (UPDATED: Removed Airbyte, Using DuckDB postgres_scanner)**

Run Order (Airflow):
1. run_spiders
2. soda_scan_check1
3. soda_scan_check2
4. soda_scan_check3
5. duckdb_sync (scripts/sync_pg_to_duckdb.py)
6. dbt_run
7. dbt_test

DuckDB Sync (local execution):
- Full refresh:
  - Windows: `set SYNC_MODE=full & python scripts/sync_pg_to_duckdb.py`
- Incremental (default, cursor=scraped_at):
  - `python scripts/sync_pg_to_duckdb.py`

Env vars:
- DUCKDB_PATH: path to .duckdb file
- DUCKDB_SCHEMA: schema in DuckDB (default: raw)
- PG_TABLE: source table in Postgres (default: jobs)
- PG_CURSOR_COLUMN: timestamp column (default: scraped_at)
- POSTGRES_HOST/PORT/DB/USER/PASSWORD

Notes:
- No Airbyte required. Connector issues on Windows avoided.
- Single-writer discipline for DuckDB.
- Parameterize Airflow `duckdb_sync` via env if needed.
