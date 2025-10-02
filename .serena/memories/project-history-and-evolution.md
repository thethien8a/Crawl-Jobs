**HISTORY UPDATE (September 2025 - Bronze-Silver-Gold Architecture)**

**Recent Changes:**
- ✅ dbt-duckdb project created (dbt_crawjob/) with portable profiles.yml
- ✅ Bronze layer: bronze.jobs (raw data from sync)
- ✅ Silver layer: silver.stg_jobs (normalized data)
- ✅ Gold layer: gold.dim_company, gold.fct_jobs (analytics-ready)
- ✅ Updated README and requirements
- ✅ Full codebase scan completed - all memories synchronized

**Adopted Bronze-Silver-Gold for ELT:**
- Bronze: raw data from PostgreSQL sync (incremental)
- Silver: normalized data (dbt models)
- Gold: analytics marts (dim/fact for BI)

**Current Architecture:**
Scrapy → PostgreSQL (raw) → Soda Core → DuckDB postgres_scanner → dbt-duckdb (Bronze-Silver-Gold) → Superset
FastAPI → PostgreSQL (serving API)

**dbt-duckdb Integration:**
- Portable setup (profiles.yml in repo)
- Incremental models with merge strategy
- Tests for data quality
- CI ready with DBT_PROFILES_DIR

**Key Milestones:**
1. ✅ Initial project setup with 10 spiders
2. ✅ PostgreSQL integration and Soda validation
3. ✅ DuckDB EL pipeline setup
4. ✅ Bronze-Silver-Gold layers in DuckDB
5. ✅ dbt-duckdb project creation
6. ✅ Simplified development tooling
7. 🔄 API migration to PostgreSQL (pending)
8. ⏳ Superset dashboard integration

**Future Direction:**
- Complete dbt models (dim_location, dim_industry, agg tables)
- Integrate dbt into Airflow DAG
- Connect Superset to DuckDB gold layer
- Add advanced dbt tests and snapshots