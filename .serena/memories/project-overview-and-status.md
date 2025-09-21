**PROJECT IDENTITY**
- **Purpose:** End-to-end data pipeline scraping, validating, transforming, and serving job data from 10+ Vietnamese job sites
- **Tech Stack (Current):** Python, Scrapy, Selenium, PostgreSQL, Airbyte (EL), DuckDB, dbt-duckdb, FastAPI, Vanilla JS, Docker, Soda Core, Airflow, Superset
- **Data Quality:** Soda Core sequential checks (3 layers) + dbt tests (business rules)

**CURRENT STATE (UPDATED: September 2025)**
- **Status:** Active development with Airflow orchestration; Airbyte chosen for EL from PostgreSQL → DuckDB; transforms run in DuckDB via dbt-duckdb
- **Architecture:** Scrapy → PostgreSQL (raw) → Soda Core → Airbyte (sync) → DuckDB → dbt-duckdb (transform + tests) → Superset
- **Recent Changes:**
  - ✅ Switched to Airbyte for EL: PostgreSQL → DuckDB
  - ✅ Updated README and plan diagrams to reflect dbt-duckdb only (no cross-DB dbt)
  - ✅ Reinforced sequential Soda validation (check1 → check2 → check3)
  - ✅ Makefile removed - not needed for current workflow
  - ✅ pyproject.toml simplified to Black + isort only

**NEXT STEPS**
1. Configure and schedule Airbyte syncs in Airflow (per table, incremental).
2. Create dbt-duckdb project and models (staging/dim/fact) in DuckDB.
3. Wire Superset to DuckDB file/URI.

**STRENGTHS**
- Clear separation OLTP/OLAP
- Lightweight, cost-efficient analytics with DuckDB
- Robust quality gates before sync and transform
- Simplified tooling (Black + isort only)

**AREAS TO IMPROVE**
- Airbyte deployment & monitoring
- Single-writer discipline on DuckDB files
- Alerting on sync/transform failures
- API still uses SQL Server instead of PostgreSQL (inconsistency)