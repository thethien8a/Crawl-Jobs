**PROJECT STRUCTURE OVERVIEW (REFRESHED: September 2025 - Current on-disk layout)**

Key updates (paths corrected):
- Bronze sync script is now at `sync_pg_to_duck/sync.py` (not DuckDB/src or pg_to_duckdb)
- dbt project at `dbt_crawjob/` with Bronze/Silver/Gold models

Directory highlights:
- `CrawlJob/` spiders, pipelines, items, settings, utils
- `airflow/dags/crawljob_pipeline.py` (DAG)
- `sync_pg_to_duck/sync.py` (Postgres → DuckDB Bronze incremental sync)
- `DuckDB/warehouse.duckdb`, `DuckDB/test/test_connect.py`
- `dbt_crawjob/` (portable dbt project)
  - `models/bronze/schema.yml`
  - `models/silver/stg_jobs.sql`, `models/silver/schema.yml`
  - `models/gold/dim_company.sql`, `models/gold/fct_jobs.sql`, `models/gold/schema.yml`
  - `models/sources.yml`
  - `profiles.yml`, `dbt_project.yml`
- `soda/checks/*.yml`, `soda/configuration.yml`
- `README.md`, `requirements.txt`, `plan/DATA_ENGINEERING_STACK_PLAN.md`

Navigation shortcuts:
- Bronze Sync: `sync_pg_to_duck/sync.py`
- dbt Project: `dbt_crawjob/` (profiles.yml, models, tests)
- DuckDB: `DuckDB/warehouse.duckdb` (query via `DuckDB/test/test_connect.py`)
- DAG: `airflow/dags/crawljob_pipeline.py`

Env of interest:
- `DUCKDB_PATH`, `DBT_PROFILES_DIR`, `POSTGRES_*`, optional `SYNC_DATE`
