**HISTORY UPDATE (September 2025)**

Changes:
- Removed Airbyte EL due to Windows/Docker connector issues (temp file mount, Java connector).
- Implemented DuckDB `postgres_scanner`-based EL via `scripts/sync_pg_to_duckdb.py`.
- Updated Airflow DAG to include `duckdb_sync` task in place of Airbyte.
- Requirements updated with duckdb, duckdb-engine.
- Documentation and operations guide updated accordingly.

Rationale:
- Simplify EL path, reduce operational friction on Windows.
- Keep architecture lightweight while preserving OLAP flow in DuckDB.
