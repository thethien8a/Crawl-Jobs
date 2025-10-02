**PROJECT OVERVIEW (REFRESHED: September 2025)**

Pipeline:
- Scrapy → PostgreSQL (raw) → Soda Core → DuckDB (Bronze via sync_pg_to_duck/sync.py) → dbt-duckdb (Silver/Gold) → Superset
- FastAPI → PostgreSQL (serving API)

Current state:
- Bronze: `bronze.jobs` populated via incremental sync (MERGE-by-day semantics)
- Silver: `silver.stg_jobs` model ready (incremental, cleaned/normalized)
- Gold: `gold.dim_company`, `gold.fct_jobs` models ready
- dbt project: `dbt_crawjob/` with portable `profiles.yml` (use `--profiles-dir .`)
- DuckDB file: `DuckDB/warehouse.duckdb` (query with `DuckDB/test/test_connect.py`)

Next steps:
- Run dbt: `dbt run --profiles-dir . -s silver.stg_jobs gold.dim_company gold.fct_jobs`
- Add more dims (location, industry) and aggregates (agg_jobs_daily)
- Integrate dbt tasks into Airflow DAG
- Connect Superset to Gold schema in DuckDB
