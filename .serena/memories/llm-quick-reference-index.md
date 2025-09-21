**QUICK REFERENCE INDEX (UPDATED: September 2025 - Post-Makefile Removal)**

**CORE COMPONENTS & SYMBOLS**

**Main Classes:**
- `JobItem(scrapy.Item)`: Base item class in `CrawlJob/items.py`
- `CrawljobPipeline`: Basic validation pipeline in `CrawlJob/pipelines.py`
- `PostgreSQLPipeline`: Database storage pipeline in `CrawlJob/pipelines.py`
- `SeleniumMiddleware`: Browser automation in `CrawlJob/selenium_middleware.py`

**Spider Classes (10 total):**
- `CareerlinkSpider`: `CrawlJob/spiders/careerlink_spider.py`
- `CareervietSpider`: `CrawlJob/spiders/careerviet_spider.py`
- `ItviecSpider`: `CrawlJob/spiders/itviec_spider.py`
- `Job123Spider`: `CrawlJob/spiders/job123_spider.py`
- `JobokoSpider`: `CrawlJob/spiders/joboko_spider.py`
- `JobsgoSpider`: `CrawlJob/spiders/jobsgo_spider.py`
- `JobstreetSpider`: `CrawlJob/spiders/jobstreet_spider.py`
- `LinkedinSpider`: `CrawlJob/spiders/linkedin_spider.py`
- `TopcvSpider`: `CrawlJob/spiders/topcv_spider.py`
- `VietnamworksSpider`: `CrawlJob/spiders/vietnamworks_spider.py`

**API Endpoints:**
- `GET /health`: Health check endpoint in `api/main.py`
- `GET /jobs`: Retrieve job listings with pagination in `api/main.py`
- `get_conn()`: Database connection function in `api/main.py`
- `jobs()`: Jobs data retrieval function in `api/main.py`

**Key Functions:**
- `parse_job(response)`: Extract job data from detail pages (all spiders)
- `parse_search(response)`: Extract job URLs from search results (all spiders)
- `start_requests()`: Generate initial search URLs with keyword support
- `process_item(item, spider)`: Process and store scraped items (PostgreSQLPipeline)
- `validate_item(item)`: Check data quality and completeness
- `main()`: Spider execution script in `run_spider.py`

**Airflow DAG Tasks:**
- `run_spiders`: Execute all job spiders
- `soda_scan_check1`: Schema and basic validation
- `soda_scan_check2`: Source-specific field validation
- `soda_scan_check3`: Spider coverage validation
- `dbt_run`: Data transformation
- `dbt_test`: Business rule validation

**CONFIGURATION CONSTANTS**

**Scrapy Settings (`CrawlJob/settings.py`):**
- `BOT_NAME = "CrawlJob"`
- `ROBOTSTXT_OBEY = False`
- `CONCURRENT_REQUESTS = 16`
- `DOWNLOAD_DELAY = 2`
- `COOKIES_ENABLED = False`
- `ITEM_PIPELINES = {"CrawljobPipeline": 200, "PostgreSQLPipeline": 300}`

**Database Settings:**
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`
- `POSTGRES_USER`, `POSTGRES_PASSWORD`

**Soda Configuration:**
- Data source: `job_database`
- Check files: `raw_jobs_check1.yml`, `raw_jobs_check2.yml`, `raw_jobs_check3.yml`
- Config file: `soda/configuration.yml`

**Code Quality Tools (Simplified):**
- `black .` - Format code automatically
- `isort .` - Sort import statements
- No flake8/mypy (removed from pyproject.toml)

**COMMON PATTERNS & SNIPPETS**

**Spider Template (with keyword search):**
```python
import scrapy
from datetime import datetime
from ..items import JobItem

class SiteSpider(scrapy.Spider):
    name = 'site_spider'
    allowed_domains = ['site.com']

    def __init__(self, keyword=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keyword = keyword or 'data analyst'
        self._unique_job_urls = set()

    def start_requests(self):
        search_url = f"https://site.com/search?q={self.keyword}"
        yield scrapy.Request(url=search_url, callback=self.parse_search,
                           meta={'keyword': self.keyword})

    def parse_search(self, response):
        job_urls = response.css('a.job-link::attr(href)').getall()
        for url in job_urls:
            if url not in self._unique_job_urls:
                self._unique_job_urls.add(url)
                yield response.follow(url, callback=self.parse_job,
                                    meta=response.meta)

    def parse_job(self, response):
        yield JobItem(
            job_title=response.css('h1.job-title::text').get(),
            company_name=response.css('.company-name::text').get(),
            location=response.css('.location::text').get(),
            job_description=response.css('.description').get(),
            salary=response.css('.salary::text').get(),
            source_site=self.name,
            scraped_at=datetime.now()
        )
```

**Pipeline Pattern (PostgreSQL):**
```python
import psycopg2
import os
from scrapy.exceptions import DropItem

class PostgreSQLPipeline:
    def __init__(self):
        self.connection = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            database=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD')
        )

    def process_item(self, item, spider):
        # Validate required fields
        required_fields = ['job_title', 'company_name', 'location', 'job_description']
        for field in required_fields:
            if not item.get(field):
                raise DropItem(f"Missing required field: {field}")

        # Insert to database
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO jobs (
                    job_title, company_name, location, job_description,
                    salary, source_site, scraped_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                item['job_title'], item['company_name'], item['location'],
                item['job_description'], item.get('salary'), item['source_site'],
                item['scraped_at']
            ))
        self.connection.commit()
        return item
```

**Sequential Soda Validation Commands:**
```bash
# Check 1: Schema and basic validation
soda scan -d job_database -c soda/configuration.yml soda/checks/raw_jobs_check1.yml

# Check 2: Source-specific validation
soda scan -d job_database -c soda/configuration.yml soda/checks/raw_jobs_check2.yml

# Check 3: Coverage validation
soda scan -d job_database -c soda/configuration.yml soda/checks/raw_jobs_check3.yml
```

**Manual Development Workflow (Without Makefile):**
```bash
# Setup environment
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# Start database
docker-compose up -d db

# Run spiders
python run_spider.py --spider all --keyword "Data Engineer"

# Check data quality
soda scan -d job_database -c soda/configuration.yml soda/checks/raw_jobs_check1.yml
soda scan -d job_database -c soda/configuration.yml soda/checks/raw_jobs_check2.yml
soda scan -d job_database -c soda/configuration.yml soda/checks/raw_jobs_check3.yml

# Sync to DuckDB
python PyAirbyte/airbyte.py

# Start API
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Code quality
black .
isort .
```

**DATA QUALITY CHECKS (3-Layer Sequential)**

**Check 1 (Schema Gate):**
- Required columns: job_url, job_title, company_name, scraped_at
- No duplicates: company_name + job_title + source_site
- No missing values: job_title, company_name, location, job_description
- Data quality gate (stops pipeline if validation fails)

**Check 2 (Source-Specific):**
- Per-source field validation (careerlink.vn, careerviet.vn, itviec.com, etc.)
- Validates presence of source-specific fields (salary, requirements, benefits)
- Ensures data completeness for each job platform

**Check 3 (Coverage):**
- Spider coverage validation (ensures all 10 spiders collected data)
- Count distinct source_site = 10
- Cross-platform data completeness checks

**FREQUENTLY USED COMMANDS (Without Makefile)**

**Run Spiders:**
```bash
# Individual spider
scrapy crawl vietnamworks_spider -o outputs/vietnamworks.json

# All spiders with keyword
python run_spider.py --spider all --keyword "data analyst"

# Airflow DAG execution (when Airflow is set up)
airflow dags trigger crawljob_pipeline
```

**Data Quality (Sequential):**
```bash
# Manual sequential validation
soda scan -d job_database -c soda/configuration.yml soda/checks/raw_jobs_check1.yml
soda scan -d job_database -c soda/configuration.yml soda/checks/raw_jobs_check2.yml
soda scan -d job_database -c soda/configuration.yml soda/checks/raw_jobs_check3.yml
```

**Code Quality (Simplified):**
```bash
# Format code
black .

# Sort imports
isort .

# Check formatting only
black --check .
isort --check-only .
```

**Development:**
```bash
# Debug HTML responses
python debug/HTML_export_debug.py

# Test database connection
python test/test_connect_Postgre.py

# Start API server
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# View data visualization
python test/export_data_to_html_en.py
start test/display_data_dynamic.html
```

**COMMON GOTCHAS**

**Dynamic Content Issues:**
- Use Selenium for JavaScript-rendered content
- Add WebDriverWait for elements to load
- Check for anti-bot measures and CAPTCHAs
- Update ChromeDriver version regularly

**Database Connection Issues:**
- Check environment variables in `CrawlJob/settings.py`
- Ensure PostgreSQL is running and accessible
- Use connection pooling for concurrent requests
- Handle connection timeouts and reconnections

**Sequential Validation Failures:**
- Check1 failures: Verify required fields are populated in spiders
- Check2 failures: Ensure source-specific fields are extracted correctly
- Check3 failures: Verify all spiders are running and collecting data

**Airflow DAG Issues:**
- Check file paths in bash_command (use absolute paths in containers)
- Verify environment variables are available to Airflow workers
- Test individual commands manually before DAG execution

**Spider Blocking Issues:**
- Increase DOWNLOAD_DELAY in settings.py (currently 2 seconds)
- Rotate user agents and browser fingerprints
- Add random delays between requests
- Monitor for CAPTCHAs and implement solving logic

**Code Quality Issues:**
- Run `black .` and `isort .` before committing
- Check Black/isort exclude patterns in pyproject.toml
- Use consistent Python version (3.12 as configured)

**DATA STRUCTURES**

**Job Item Fields (CrawlJob/items.py):**
```python
{
    'job_title': str,           # Job title (required)
    'company_name': str,        # Company name (required)
    'location': str,            # Job location (required)
    'job_description': str,     # Job description (required)
    'salary': str,              # Salary information
    'job_type': str,            # Full-time, part-time, etc.
    'experience_level': str,    # Junior, Senior, etc.
    'education_level': str,     # Education requirements
    'job_industry': str,        # Industry sector
    'job_position': str,        # Position level
    'requirements': str,        # Job requirements
    'benefits': str,            # Job benefits
    'job_deadline': str,        # Application deadline
    'source_site': str,         # Source website (required)
    'job_url': str,             # Job URL (required)
    'search_keyword': str,      # Search keyword used
    'scraped_at': datetime       # Scraping timestamp (required)
}
```

**Spider Settings Pattern:**
```python
def __init__(self, keyword=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.keyword = keyword or 'data analyst'
    self._count_page = 0
    self._max_page = 3  # Limit pages per spider
    self._unique_job_urls = set()  # Deduplication
```

**DEBUGGING SYMBOLS**

**Key Debug Points:**
- `len(response.css('selector'))` - Count selector matches
- `response.css('selector::text').get()` - Extract text content
- `response.css('selector::attr(href)').getall()` - Extract URLs
- `item` in pipeline - Inspect processed data before database insert
- `self._unique_job_urls` - Check deduplication logic

**Error Handling Patterns:**
```python
try:
    # Extract job data
    title = response.css('h1.title::text').get()
    if not title:
        self.logger.warning(f"No title found for {response.url}")
        return
    # Process data...
except Exception as e:
    self.logger.error(f"Error parsing job {response.url}: {e}")
    # Continue to next job
```

**LOGGING PATTERNS:**
- `INFO`: General progress (\"Found 25 job listings\")
- `WARNING`: Potential issues (\"Selector not found, trying fallback\")
- `ERROR`: Serious problems (\"Database connection failed\")
- `DEBUG`: Detailed diagnostic (\"Processing URL: https://...\")

**FILE LOCATIONS BY PURPOSE**
- **Spiders:** `CrawlJob/spiders/` (10 specialized crawlers)
- **Pipelines:** `CrawlJob/pipelines.py` (CrawljobPipeline + PostgreSQLPipeline)
- **Settings:** `CrawlJob/settings.py` (Scrapy + database config)
- **Items:** `CrawlJob/items.py` (JobItem definition)
- **Middleware:** `CrawlJob/selenium_middleware.py` (Browser automation)
- **API:** `api/main.py` (FastAPI endpoints)
- **Orchestration:** `airflow/dags/crawljob_pipeline.py` (Sequential DAG)
- **Data Quality:** `soda/checks/` (3 sequential validation files)
- **Logs:** `logs/` (Timestamped crawl logs)
- **Outputs:** `outputs/` (JSON output files)
- **Tests:** `test/` (Connection tests, visualization)
- **Web UI:** `web/` (Dashboard and API integration)
- **Code Quality:** `pyproject.toml` (Black + isort configuration)