**ARCHITECTURE OVERVIEW (UPDATED: DuckDB postgres_scanner EL)**

Data Flow:
Scrapy → PostgreSQL (raw) → Soda Core → DuckDB postgres_scanner (EL) → dbt-duckdb (transform + tests) → Superset
FastAPI → PostgreSQL (serving API)

Key Decisions:
- Removed Airbyte due to Windows/Docker friction with Java connectors.
- Adopted DuckDB `postgres_scanner` for EL: simpler, stable, no external services.

Components:
1) Scraping (Scrapy + Selenium)
2) OLTP (PostgreSQL)
3) Data Quality (Soda Core check1/2/3)
4) EL (DuckDB postgres_scanner via `scripts/sync_pg_to_duckdb.py`)
5) Transform (dbt-duckdb)
6) BI (Superset on DuckDB)
7) Serving (FastAPI on PostgreSQL)

Airflow DAG Pattern:
- run_spiders → soda_check1 → soda_check2 → soda_check3 → duckdb_sync → dbt_run → dbt_test → publish

Operational Patterns:
- Full vs Incremental modes controlled by `SYNC_MODE` env.
- Cursor column default `scraped_at`; override via env.
- Primary keys/unique constraints enforced in downstream dbt models if needed.

Risks & Mitigations:
- File lock on DuckDB: avoid concurrent writers, serialize Airflow steps.
- Incremental correctness: ensure cursor column monotonic per job; add dbt tests.
- Network/auth to Postgres: validate with psycopg2 before sync.
