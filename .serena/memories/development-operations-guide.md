**OPERATIONS (UPDATED: September 2025 - Post-Makefile Removal)**

**Run Order (Airflow):**
1. run_spiders
2. soda_scan_check1
3. soda_scan_check2
4. soda_scan_check3
5. airbyte_sync_postgres_to_duckdb
6. dbt_run (dbt-duckdb project)
7. dbt_test
8. notify/publish

**Airbyte Sync (CLI/API):**
- Define connection: Source=PostgreSQL, Destination=DuckDB
- Schedule via Airflow using Airbyte API:
  - Trigger: POST /api/v1/connections/sync
  - Monitor: GET job status until Succeeded/Failed

**dbt-duckdb:**
- profiles.yml points to DuckDB path (e.g., D:/warehouse.duckdb)
- Run:
```bash
cd path/to/dbt_duckdb_project
 dbt run && dbt test
```

**Superset:**
- SQLAlchemy URI: duckdb:///D:/path/to/warehouse.duckdb

**Code Quality (Simplified):**
- Format code: `black .` or `black CrawlJob api PyAirbyte airflow`
- Sort imports: `isort .` or `isort CrawlJob api PyAirbyte airflow`
- No flake8/mypy configured (removed from pyproject.toml)

**Gotchas:**
- Ensure only one writer to DuckDB
- Keep Airbyte and dbt on separate steps
- Pass env vars for Postgres credentials to Soda and Airbyte
- Log retention for Soda/dbt/Airbyte artifacts

**Development Workflow (Without Makefile):**
```bash
# Setup
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy env.example .env

# Development
docker-compose up -d db
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Testing
python -m pytest test/ -v

# Code quality
black .
isort .

# Production
python run_spider.py --spider all --keyword "Data Engineer"
python PyAirbyte/airbyte.py

# Data quality
soda scan -d job_database -c soda/configuration.yml soda/checks/raw_jobs_check1.yml
soda scan -d job_database -c soda/configuration.yml soda/checks/raw_jobs_check2.yml
soda scan -d job_database -c soda/configuration.yml soda/checks/raw_jobs_check3.yml
```