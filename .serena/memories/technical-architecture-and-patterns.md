**PROCESSING LAYER (UPDATED)**
- Two-layer validation pattern:
  1) Raw Gate (Soda Core): validate PostgreSQL raw tables immediately after ingestion. Fail-fast halts pipeline.
     - Command: `soda scan -d postgres_db -c soda/configuration.yml soda/checks/raw_jobs.yml`
  2) Business Validation (dbt tests): run after `dbt run` on staging/dim/fact/agg models.
- ELT remains: Scrapy → Postgres (raw) → dbt (transform) → DuckDB (OLAP).
- Serving unchanged: FastAPI → Postgres (OLTP); Superset → DuckDB (OLAP).

**AIRFLOW PATTERN (RECOMMENDED)**
- Tasks: `run_spiders` → `soda_scan_raw` → `dbt_run` → `dbt_test` → `publish_duckdb`
- Gate: if `soda_scan_raw` fails → alert and stop.

**RATIONALE**
- Keep validation close to its context: raw quality at the source (Soda) and business rules within models (dbt).