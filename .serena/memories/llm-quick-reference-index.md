**QUICK REFERENCE (DuckDB postgres_scanner EL)**

Sync Script:
- `scripts/sync_pg_to_duckdb.py`
- Modes: `SYNC_MODE=full` or `incremental` (default)
- Env: DUCKDB_PATH, DUCKDB_SCHEMA (default raw), PG_TABLE (default jobs), PG_CURSOR_COLUMN (default scraped_at), POSTGRES_*

Airflow Task:
- `duckdb_sync`: `python /opt/airflow/dags/scripts/sync_pg_to_duckdb.py`

Common Commands:
- Full: `set SYNC_MODE=full & python scripts/sync_pg_to_duckdb.py`
- Incremental: `python scripts/sync_pg_to_duckdb.py`

Troubleshooting:
- Ensure Postgres reachable (test via psycopg2).
- DuckDB single-writer; serialize steps.
- If incremental off-by-one, consider `>=` and persist last watermark explicitly.
