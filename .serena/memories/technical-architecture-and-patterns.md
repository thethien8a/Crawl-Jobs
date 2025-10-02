**ARCHITECTURE OVERVIEW (UPDATED: Bronze-Silver-Gold in DuckDB)**

**Data Flow:**
Scrapy → PostgreSQL (raw) → Soda Core → DuckDB postgres_scanner (bronze) → dbt-duckdb (silver/gold) → Superset
FastAPI → PostgreSQL (serving API)

**Key Decisions:**
- Implemented Bronze-Silver-Gold layers in DuckDB using dbt-duckdb
- Portable dbt setup (profiles.yml in repo for CI)
- Removed Airbyte due to Windows/Docker friction

**Components:**
1. Scraping (Scrapy + Selenium)
2. OLTP (PostgreSQL)
3. Data Quality (Soda Core check1/2/3)
4. EL (DuckDB postgres_scanner via bronze.py)
5. Bronze (raw data)
6. Silver (normalized data)
7. Gold (analytics marts)
8. BI (Superset on DuckDB)
9. Serving (FastAPI on PostgreSQL)

**dbt-duckdb Layers:**
- Bronze: bronze.jobs (raw from sync)
- Silver: silver.stg_jobs (normalized)
- Gold: gold.dim_company, gold.fct_jobs (analytics-ready)

**Airflow DAG Pattern:**
- run_spiders → soda_check1 → soda_check2 → soda_check3 → duckdb_sync → dbt_run_silver → dbt_run_gold → dbt_test

**Operational Patterns:**
- Incremental models with unique_key and is_incremental() filter
- Portable profiles.yml in repo
- DBT_PROFILES_DIR for CI

**Risks & Mitigations:**
- Schema evolution: dbt schema.yml with tests
- Incremental correctness: dbt tests + Soda gates
- CI: DBT_PROFILES_DIR env override