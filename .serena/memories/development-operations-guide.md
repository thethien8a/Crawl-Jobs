**OPERATIONS GUIDE (REFRESHED: September 2025)**

Daily run (manual):
1) Crawl → PostgreSQL
2) Soda checks (raw)
3) Sync Bronze: `python sync_pg_to_duck/sync.py`
4) dbt Silver/Gold:
   - `cd dbt_crawjob && dbt debug --profiles-dir .`
   - `dbt run --profiles-dir . -s silver.stg_jobs`
   - `dbt run --profiles-dir . -s gold.dim_company gold.fct_jobs`
   - `dbt test --profiles-dir .`
5) BI: Superset on DuckDB (gold schema)

Airflow (suggested):
- run_spiders → soda_scan_check1/2/3 → duckdb_sync → dbt_run_silver → dbt_run_gold → dbt_test

Env:
- DUCKDB_PATH, DBT_PROFILES_DIR, POSTGRES_HOST/PORT/DB/USER/PASSWORD, optional SYNC_DATE

Troubleshooting:
- DuckDB parser errors → split CTE/CREATE/MERGE into separate execute() calls
- dbt not finding profiles → set `--profiles-dir .` or `DBT_PROFILES_DIR`
- Empty silver/gold → ensure bronze.jobs has data; run `dbt run` again
