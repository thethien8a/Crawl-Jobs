**PROJECT STRUCTURE OVERVIEW (UPDATED: September 2025)**

**Key Architecture Updates:**
- Removed `PyAirbyte/` sync script; added `pg_to_duckdb/sync_pg_to_duckdb.py` using DuckDB postgres_scanner
- Airflow DAG now calls DuckDB sync step `duckdb_sync` instead of Airbyte
- Requirements updated to include `duckdb`, `duckdb-engine`
- API layer exists but currently connects to PostgreSQL (should connect to DuckDB for analytics)

**Directory Structure:**
```
CrawlJob/                           # Main Scrapy project
├── spiders/                        # 10 Vietnamese job site spiders
│   ├── topcv_spider.py            # TopCV - most sophisticated (JS parsing)
│   ├── careerlink_spider.py       # CareerLink
│   ├── careerviet_spider.py       # CareerViet
│   ├── itviec_spider.py           # ITviec
│   ├── job123_spider.py           # 123Job
│   ├── joboko_spider.py           # JobOKO (uses Selenium)
│   ├── jobsgo_spider.py           # JobsGo
│   ├── jobstreet_spider.py        # JobStreet
│   ├── linkedin_spider.py         # LinkedIn
│   └── vietnamworks_spider.py     # VietnamWorks (uses Selenium)
├── items.py                        # JobItem data model (15+ fields)
├── pipelines.py                    # PostgreSQL pipeline with UPSERT
├── selenium_middleware.py         # Chrome/Selenium for JS sites
├── settings.py                     # Scrapy configuration + DB settings
└── utils.py                        # Helper functions

pg_to_duckdb/                       # New DuckDB sync layer
└── sync_pg_to_duckdb.py           # Incremental sync: PostgreSQL → DuckDB

airflow/dags/                       # Orchestration
└── crawljob_pipeline.py           # Main DAG: spiders → soda → duckdb → dbt

soda/checks/                        # Data quality validation
├── raw_jobs_check1.yml            # Schema, required fields, duplicates
├── raw_jobs_check2.yml            # Cross-spider completeness
└── raw_jobs_check3.yml            # Site-specific field completion

api/                                # Serving layer
└── main.py                        # FastAPI REST API (currently PostgreSQL)

web/                               # Frontend
├── index.html                    # Bootstrap-based job search UI
├── css/                          # Styling
├── js/                           # API integration, UI logic
└── README.md                     # Frontend documentation

Configuration Files:
├── docker-compose.yml            # Container orchestration
├── requirements.txt              # Python dependencies
├── pyproject.toml               # Project configuration
└── scrapy.cfg                   # Scrapy project settings

Data & Logs:
├── DuckDB/                       # DuckDB files location
├── logs/                         # Scrapy crawl logs
├── outputs/                      # JSON export outputs
└── jobs.json                    # Sample data
```

**Navigation Shortcuts:**
- **Sync Script:** `pg_to_duckdb/sync_pg_to_duckdb.py`
- **Main DAG:** `airflow/dags/crawljob_pipeline.py` (task: `duckdb_sync`)
- **Quality Checks:** `soda/checks/` (3 sequential YAML files)
- **API Endpoint:** `api/main.py` (FastAPI on port 8000)
- **Frontend:** `web/index.html` (Bootstrap UI)
- **Data Model:** `CrawlJob/items.py` (JobItem with 15+ fields)
- **Selenium Middleware:** `CrawlJob/selenium_middleware.py` (Chrome automation)

**Configuration via Environment:**
- `DUCKDB_PATH`: Path to .duckdb file
- `DUCKDB_SCHEMA`: Schema in DuckDB (default: staging)
- `PG_TABLE`: Source table in Postgres (default: jobs)
- `PG_CURSOR_COLUMN`: Timestamp column (default: scraped_at)
- `SYNC_MODE`: `incremental` (default) or `full`
- PostgreSQL connection settings (HOST, PORT, DB, USER, PASSWORD)

**Key Files for Understanding:**
1. `CrawlJob/spiders/topcv_spider.py` - Most sophisticated spider with JS parsing
2. `pg_to_duckdb/sync_pg_to_duckdb.py` - DuckDB postgres_scanner implementation
3. `soda/checks/raw_jobs_check3.yml` - Site-specific validation rules
4. `CrawlJob/items.py` - Complete data model
5. `airflow/dags/crawljob_pipeline.py` - Full pipeline orchestration