**PROJECT STRUCTURE OVERVIEW (UPDATED: September 2025)**

Key updates:
- Removed `PyAirbyte/` sync script; added `scripts/sync_pg_to_duckdb.py` using DuckDB postgres_scanner.
- Airflow DAG now calls DuckDB sync step `duckdb_sync` instead of Airbyte.
- Requirements updated to include `duckdb`, `duckdb-engine`.

Navigation shortcuts:
- Sync script: `scripts/sync_pg_to_duckdb.py`
- Airflow DAG: `airflow/dags/crawljob_pipeline.py` (task: `duckdb_sync`)
- Config via env: `DUCKDB_PATH`, `DUCKDB_SCHEMA` (default `raw`), `PG_TABLE` (default `jobs`), `PG_CURSOR_COLUMN` (default `scraped_at`), `SYNC_MODE` (`incremental` or `full`).
