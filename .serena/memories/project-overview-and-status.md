**PROJECT IDENTITY**
- **Purpose:** End-to-end data pipeline scraping, validating, transforming, and serving job data from 10+ Vietnamese job sites
- **Tech Stack (Current):** Python, Scrapy, Selenium, PostgreSQL, DuckDB (postgres_scanner), dbt-duckdb, FastAPI, Vanilla JS, Docker, Soda Core, Airflow, Superset
- **Data Quality:** Soda Core sequential checks (3 layers) + dbt tests (business rules)

**CURRENT STATE (UPDATED: September 2025)**
- **Status:** Active development with Airflow orchestration; Airbyte removed; EL now uses DuckDB postgres_scanner (PostgreSQL → DuckDB)
- **Architecture:** Scrapy → PostgreSQL (raw) → Soda Core → DuckDB postgres_scanner (sync) → dbt-duckdb (transform + tests) → Superset
- **Recent Changes:**
  - ✅ Replaced Airbyte with DuckDB postgres_scanner (script `scripts/sync_pg_to_duckdb.py`)
  - ✅ Updated Airflow DAG to call DuckDB sync step
  - ✅ Removed PyAirbyte files
  - ✅ Updated README and requirements
  - ✅ Code quality simplified (Black + isort)

**NEXT STEPS**
1. Parameterize sync (per table, schedule) in Airflow via env.
2. Build dbt-duckdb models (staging/dim/fact) and tests.
3. Connect Superset to DuckDB file/URI.

**STRENGTHS**
- Simpler EL on Windows (no Docker connectors)
- Clear separation OLTP/OLAP
- Robust quality gates before sync and transform

**AREAS TO IMPROVE**
- Incremental sync strategy per stream (cursor/PK choices)
- Single-writer discipline on DuckDB files
- Alerting on sync/transform failures