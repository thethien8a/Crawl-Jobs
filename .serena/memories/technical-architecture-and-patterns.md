**ARCHITECTURE OVERVIEW (UPDATED: DuckDB postgres_scanner EL)**

**Complete Data Pipeline:**
Scrapy (10 spiders) → PostgreSQL (raw) → Soda Core (3 checks) → DuckDB postgres_scanner (EL) → dbt-duckdb (transform + tests) → Superset (BI)
FastAPI (PostgreSQL) → Vanilla JS (Frontend)

**Key Architectural Decisions:**
- **Removed Airbyte:** Due to Windows/Docker friction with Java connectors
- **Adopted DuckDB postgres_scanner:** Simpler, stable, no external services
- **OLTP vs OLAP separation:** PostgreSQL for raw data, DuckDB for analytics
- **Quality-first approach:** 3-layer Soda validation before any downstream processing

**Component Details:**

1) **Scraping Layer (Scrapy + Selenium)**
   - **Spiders:** 10 specialized spiders for Vietnamese job sites
   - **Middleware:** Selenium for JS-heavy sites (joboko, vietnamworks)
   - **Patterns:** AutoThrottle rate limiting, retry logic, duplicate prevention
   - **Data Model:** Comprehensive JobItem with 15+ fields including metadata

2) **OLTP Storage (PostgreSQL)**
   - **Table:** `jobs` with UPSERT logic (ON CONFLICT DO UPDATE)
   - **Schema:** 15+ columns covering job details, metadata, timestamps
   - **Constraints:** Unique on (job_title, company_name, source_site)

3) **Data Quality Gates (Soda Core)**
   - **Check 1:** Schema validation, required fields, duplicates
   - **Check 2:** Cross-spider completeness (ensures all 10 sites scraped)
   - **Check 3:** Site-specific field completion rates
   - **Sequential:** Must pass all checks before proceeding

4) **EL Layer (DuckDB postgres_scanner)**
   - **Incremental:** Daily sync using cursor column (default: scraped_at)
   - **Method:** MERGE operations for efficient upserts
   - **Configuration:** Environment-driven (table, schema, cursor column)
   - **Single-writer:** Airflow serialization prevents conflicts

5) **Transform Layer (dbt-duckdb)**
   - **Models:** Staging → DIM/FACT architecture ready
   - **Tests:** Business rule validations
   - **Target:** Optimized for Superset BI consumption

6) **Serving Layer (FastAPI)**
   - **API:** RESTful with pagination, search, CORS
   - **Current:** Connects to PostgreSQL (OLTP)
   - **Future:** Should connect to DuckDB (OLAP) for analytics

7) **Frontend (Vanilla JS)**
   - **Framework:** Pure JavaScript with Bootstrap
   - **Features:** Search, pagination, responsive design
   - **Integration:** REST API consumption

**Operational Patterns:**
- **Airflow Orchestration:** DAG with sequential tasks
- **Environment Configuration:** Comprehensive .env support
- **Error Handling:** Retry logic at multiple levels
- **Monitoring:** Soda alerts + potential logging improvements

**Risks & Mitigations:**
- **File lock on DuckDB:** Single-writer discipline via Airflow serialization
- **Incremental correctness:** Cursor column validation + dbt tests
- **Network/auth to Postgres:** Connection validation before sync
- **Selenium reliability:** Fallback strategies + retry mechanisms