**PROJECT IDENTITY**
- **Purpose:** End-to-end data pipeline scraping, validating, transforming, and serving job data from 10+ Vietnamese job sites
- **Tech Stack (Current):** Python, Scrapy, Selenium, PostgreSQL, DuckDB (postgres_scanner), dbt-duckdb, FastAPI, Vanilla JS, Docker, Soda Core, Airflow, Superset
- **Data Quality:** Soda Core sequential checks (3 layers) + dbt tests (business rules)

**CURRENT STATE (UPDATED: September 2025)**
- **Status:** Active development with Airflow orchestration; Airbyte removed; EL now uses DuckDB postgres_scanner (PostgreSQL → DuckDB)
- **Architecture:** Scrapy → PostgreSQL (raw) → Soda Core → DuckDB postgres_scanner (sync) → dbt-duckdb (transform + tests) → Superset
- **Recent Changes:**
  - ✅ Replaced Airbyte with DuckDB postgres_scanner (script `pg_to_duckdb/sync_pg_to_duckdb.py`)
  - ✅ Updated Airflow DAG to call DuckDB sync step
  - ✅ Removed PyAirbyte files
  - ✅ Updated README and requirements
  - ✅ Code quality simplified (Black + isort)

**DATA FLOW ARCHITECTURE**
1. **Scraping Layer (Scrapy):**
   - 10 Vietnamese job site spiders: topcv, careerlink, careerviet, itviec, job123, joboko, jobsgo, jobstreet, linkedin, vietnamworks
   - Selenium middleware for JavaScript-heavy sites (joboko, vietnamworks)
   - Robust retry logic and rate limiting with AutoThrottle
   - Data stored in PostgreSQL with UPSERT logic

2. **Quality Gates (Soda Core):**
   - Check 1: Schema validation, missing data, duplicates
   - Check 2: Ensure all 10 spiders collected data
   - Check 3: Site-specific field completion validation

3. **EL Layer (DuckDB postgres_scanner):**
   - Incremental sync by date (default cursor: scraped_at)
   - MERGE operations for upsert logic
   - Single schema approach (staging.jobs)

4. **Transform Layer (dbt-duckdb):**
   - Staging → DIM/FACT models
   - Business rule validations
   - Ready for Superset BI layer

5. **Serving Layer (FastAPI):**
   - REST API with pagination and search
   - CORS enabled for web frontend
   - Currently connects to PostgreSQL (OLTP)

**NEXT STEPS**
1. Parameterize sync (per table, schedule) in Airflow via env.
2. Build dbt-duckdb models (staging/dim/fact) and tests.
3. Connect Superset to DuckDB file/URI.

**STRENGTHS**
- Simpler EL on Windows (no Docker connectors)
- Clear separation OLTP/OLAP
- Robust quality gates before sync and transform
- Comprehensive coverage of Vietnamese job market

**AREAS TO IMPROVE**
- Incremental sync strategy per stream (cursor/PK choices)
- Single-writer discipline on DuckDB files
- Alerting on sync/transform failures