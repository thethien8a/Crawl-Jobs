**PROJECT IDENTITY (UPDATED)**
- **Purpose:** A comprehensive data pipeline to scrape, validate (2 layers), transform, and serve job data from 10 VN job sites.
- **Tech Stack (Current):** Python, Scrapy, Selenium, PostgreSQL, FastAPI, Vanilla JS, Docker.
- **Data Quality (NEW):** Soda Core (raw gating) + dbt tests (business rules).

**CURRENT STATE (CHANGES)**
- Replaced Great Expectations with a hybrid validation:
  - Layer 1 (Raw Gating): Soda Core scanning PostgreSQL raw tables.
  - Layer 2 (Post-Transform): dbt built-in tests + dbt-expectations where needed.
- Added `soda/configuration.yml` and `soda/checks/raw_jobs.yml`.
- Updated `requirements.txt`: removed `great-expectations`, added `soda-core`, `soda-core-postgres`.

**NEXT STEPS**
1) Integrate Airflow DAG chain: `soda scan` → `dbt run` → `dbt test`.
2) Expand Soda checks to additional raw tables and dimensions.
3) Add dbt-expectations tests for critical models/columns.