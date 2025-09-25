**CRITICAL SYMBOLS & PATTERNS (UPDATED: September 2025)**

**Key Classes & Functions:**

1) **Data Models:**
   - `JobItem` (CrawlJob/items.py:9) - Main data model with 15+ fields
   - Comprehensive fields: job_title, company_name, salary, location, job_type, experience_level, education_level, job_industry, job_position, job_description, requirements, benefits, job_deadline, source_site, job_url, search_keyword, scraped_at

2) **Spider Patterns:**
   - `TopcvSpider` (CrawlJob/spiders/topcv_spider.py:10) - Most sophisticated spider
     - JavaScript object extraction: `_extract_from_js_object()` method
     - Dual parsing: Brand pages vs regular job pages
     - Advanced retry logic with exponential backoff
   - `SeleniumMiddleware` (CrawlJob/selenium_middleware.py:21) - Chrome automation
     - Handles joboko.vn and vietnamworks.com (JS-heavy sites)
     - Anti-detection measures (webdriver hiding)
     - Smart waiting for dynamic content

3) **Pipeline Patterns:**
   - `PostgreSQLPipeline` (CrawlJob/pipelines.py:23) - Database storage
     - UPSERT logic with ON CONFLICT DO UPDATE
     - Connection pooling and error handling
     - Table creation with proper constraints

4) **Sync Patterns:**
   - `incremental_by_timestamp()` (pg_to_duckdb/sync_pg_to_duckdb.py:22)
     - DuckDB postgres_scanner implementation
     - MERGE operations for efficient upserts
     - Environment-driven configuration

5) **Quality Validation:**
   - Soda checks in `soda/checks/` directory
     - Check1: Schema validation, required fields, duplicates
     - Check2: Cross-spider completeness (ensures 10 sites)
     - Check3: Site-specific field completion rates

6) **API Patterns:**
   - FastAPI in `api/main.py` with pagination and search
   - Currently connects to PostgreSQL (should use DuckDB for analytics)

**Common Patterns:**
- **Environment Configuration:** Extensive use of python-dotenv
- **Error Handling:** Retry mechanisms at multiple levels
- **Rate Limiting:** AutoThrottle with exponential backoff
- **Data Validation:** Multi-layer validation (Soda + dbt tests)
- **Incremental Processing:** Cursor-based incremental syncs

**Important Configuration Variables:**
- Database connections (PostgreSQL, DuckDB paths)
- Sync parameters (table, schema, cursor column, mode)
- Scrapy settings (delays, concurrency, user agents)
- Selenium options (headless, window size, anti-detection)

**Gotchas & Important Notes:**
- DuckDB single-writer requirement (Airflow serialization)
- Selenium middleware only for specific sites (joboko, vietnamworks)
- API currently serves from PostgreSQL (OLTP) not DuckDB (OLAP)
- Soda checks are sequential and blocking
- TopCV spider has sophisticated JS parsing for window.qgTracking objects

**Testing Points:**
- All spiders should handle rate limiting gracefully
- Incremental sync should preserve data integrity
- Quality checks should catch missing data from any spider
- API should handle large result sets with pagination