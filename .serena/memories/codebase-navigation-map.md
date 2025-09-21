**PROJECT STRUCTURE OVERVIEW (UPDATED: September 2025)**

**Root Directory Structure:**
```
D:\\\\Practice\\\\Scrapy\\\\CrawlJob\\\\
├── .serena/             # Serena MCP memories and project config
├── airflow/             # Airflow DAGs (implemented orchestration)
│   └── dags/
│       └── crawljob_pipeline.py  # Sequential pipeline DAG
├── api/                 # FastAPI server (⚠️ currently uses SQL Server, not PostgreSQL)
├── CrawlJob/           # Main Scrapy project
│   ├── spiders/        # 10 job site spiders
│   ├── pipelines.py    # Data processing pipelines
│   ├── items.py        # Scrapy item definitions
│   ├── settings.py     # Scrapy configuration
│   ├── selenium_middleware.py # Browser automation
│   └── utils.py        # Helper utilities
├── debug/              # HTML debugging tools
├── docker-compose.yml  # Container orchestration
├── env.example         # Environment variables template
├── logs/               # Crawl execution logs
├── outputs/            # JSON output files
├── plan/               # Data engineering plans
├── PyAirbyte/          # EL from PostgreSQL to DuckDB
│   └── airbyte.py      # Airbyte sync script
├── pyproject.toml      # Code quality config (Black + isort only)
├── README.md           # Project documentation
├── requirements.txt    # Python dependencies
├── run_spider.py       # Spider execution script
├── scrapy.cfg         # Scrapy project config
├── scripts/            # Empty directory (reserved for future scripts)
├── soda/               # Data quality validation (sequential checks)
│   ├── checks/         # Soda Core check definitions (3 files)
│   │   ├── raw_jobs_check1.yml  # Schema + duplicates + missing values
│   │   ├── raw_jobs_check2.yml  # Source-specific validations
│   │   └── raw_jobs_check3.yml  # Spider coverage validation
│   └── configuration.yml # Soda data source config
├── test/               # Testing and data visualization
└── web/                # Frontend dashboard
    ├── css/
    ├── js/
    └── index.html
```

**DETAILED COMPONENT BREAKDOWN**

**Scrapy Project (CrawlJob/)**
- **spiders/:** 10 specialized spiders
  - careerlink_spider.py
  - careerviet_spider.py
  - itviec_spider.py
  - job123_spider.py
  - joboko_spider.py
  - jobsgo_spider.py
  - jobstreet_spider.py
  - linkedin_spider.py
  - topcv_spider.py
  - vietnamworks_spider.py

- **Core Files:**
  - items.py: Scrapy Item definitions for job data structure
  - pipelines.py: Two pipelines - CrawljobPipeline (validation) + PostgreSQLPipeline (storage)
  - settings.py: Scrapy configuration with Selenium middleware and database settings
  - selenium_middleware.py: Browser automation middleware for dynamic content
  - utils.py: Helper functions for encoding and data cleaning

**Data Quality (soda/) - Sequential Validation**
- configuration.yml: PostgreSQL connection and data source setup
- checks/:
  - raw_jobs_check1.yml: Schema validation, duplicates, missing values, data quality gate
  - raw_jobs_check2.yml: Source-specific field validation (careerlink, careerviet, itviec, etc.)
  - raw_jobs_check3.yml: Spider data coverage validation (ensures all spiders have data)

**API Layer (api/)**
- main.py: FastAPI application with job data endpoints (⚠️ Currently uses SQL Server instead of PostgreSQL)

**Orchestration (airflow/dags/)**
- crawljob_pipeline.py: Sequential DAG (spiders → soda checks → dbt run → dbt test)

**Code Quality (pyproject.toml)**
- Black: Auto code formatting (line-length=88, Python 3.12)
- isort: Import sorting (profile=black, line_length=88)

**Testing & Debug (test/)**
- HTML visualization tools for data analysis
- Database connection tests
- Data export utilities
- Jupyter notebooks for analysis

**Frontend (web/)**
- Vanilla JS dashboard for job data visualization
- CSS styling and UI components
- API integration for real-time data

**NAVIGATION SHORTCUTS**

**Find Specific Components:**
- **Job Spiders:** `CrawlJob/spiders/` - All 10 site-specific crawlers
- **Data Processing:** `CrawlJob/pipelines.py` - ETL logic and database storage (2 pipelines)
- **Data Quality:** `soda/checks/` - 3 sequential validation files
- **API Endpoints:** `api/main.py` - REST API implementation
- **Orchestration:** `airflow/dags/crawljob_pipeline.py` - Sequential pipeline execution
- **Frontend:** `web/` - Dashboard and visualization
- **Configuration:** `CrawlJob/settings.py` - Scrapy, middleware, and database config

**Common Tasks:**
- **Run Spider:** `python run_spider.py --spider <name> --keyword <term>`
- **Check Data Quality:** Sequential Soda scans (check1 → check2 → check3)
- **View Logs:** `logs/` directory with timestamped crawl logs
- **Debug HTML:** `debug/HTML_export_debug.py` for response inspection
- **Test Data:** `test/` directory with visualization tools
- **Format Code:** `black .` (auto-format all Python files)
- **Sort Imports:** `isort .` (organize import statements)

**FILE PATTERNS & CONVENTIONS**

**Spider Naming:** `{site}_spider.py` (e.g., `topcv_spider.py`)
**Soda Checks:** `raw_jobs_check{N}.yml` (sequential numbering)
**Log Files:** `crawl_{timestamp}.log`
**Output Files:** `jobs_{timestamp}.json`
**Settings:** Uppercase constants, descriptive middleware lists
**API Routes:** `/health`, `/jobs` endpoints

**DATA FLOW NAVIGATION**
1. **Entry:** `run_spider.py` → `scrapy crawl <spider>` (manual) OR Airflow DAG
2. **Scraping:** `spiders/*_spider.py` → extract job data with Selenium middleware
3. **Processing:** `pipelines.py` → validate and store to PostgreSQL
4. **Quality Check:** `soda/checks/` → sequential validation (check1 → check2 → check3)
5. **Transformation:** dbt models (planned) → business-ready data
6. **Serving:** `api/main.py` → REST API endpoints
7. **Visualization:** `web/` → dashboard display

**DEVELOPMENT WORKFLOW**
- **Add New Spider:** Create in `CrawlJob/spiders/`, inherit from scrapy.Spider
- **Modify Pipeline:** Update `CrawlJob/pipelines.py` for new processing logic
- **Add Validation:** Create new `soda/checks/raw_jobs_check4.yml` for additional validations
- **Update API:** Modify `api/main.py` for new endpoints
- **Test Changes:** Use `test/` utilities for data verification
- **Update DAG:** Modify `airflow/dags/crawljob_pipeline.py` for new steps
- **Format Code:** Run `black .` and `isort .` for consistent code style

**CONFIGURATION FILES**
- `scrapy.cfg`: Project-wide Scrapy settings
- `docker-compose.yml`: Multi-service container setup
- `env.example`: Environment variables template
- `requirements.txt`: Python package dependencies
- `soda/configuration.yml`: Data quality data source config
- `pyproject.toml`: Code quality configuration (Black + isort)
- `CrawlJob/settings.py`: Scrapy and database configuration