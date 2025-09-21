**ARCHITECTURE OVERVIEW (UPDATED: September 2025 - Post-Makefile Removal)**

**Data Flow:**
Scrapy → PostgreSQL (raw) → Soda Core (sequential checks) → Airbyte (EL) → DuckDB (OLAP) → dbt-duckdb (transform + tests) → Superset
FastAPI → PostgreSQL (serving API) ⚠️ (API currently uses SQL Server, not PostgreSQL)
Vanilla JS → FastAPI (frontend)

**Key Decisions:**
- dbt does NOT cross databases. All transforms run WITHIN DuckDB using dbt-duckdb.
- Airbyte handles EL from PostgreSQL to DuckDB (incremental where possible).
- Code quality simplified to Black + isort only (removed flake8/mypy).
- Makefile removed from project structure.

**Components:**
1) Scraping (Scrapy + Selenium)
2) OLTP (PostgreSQL)
3) Data Quality (Soda Core check1/2/3)
4) EL (Airbyte: Postgres → DuckDB)
5) Transform (dbt-duckdb)
6) BI (Superset on DuckDB)
7) Serving (FastAPI on PostgreSQL) ⚠️ (inconsistency with API using SQL Server)
8) Code Quality (Black + isort via pyproject.toml)

**Airflow DAG Pattern:**
- run_spiders → soda_check1 → soda_check2 → soda_check3 → airbyte_sync → dbt_run → dbt_test → publish

**Operational Patterns:**
- Single-writer discipline for DuckDB file
- Airbyte incremental syncs (logical replication optional for CDC)
- dbt tests on transformed models
- Superset connects via duckdb-engine URI

**Code Quality Patterns (Simplified):**
- Black: Auto-formatting (line-length=88, Python 3.12 target)
- isort: Import sorting (profile=black, multi-line output)
- Excludes: .git, __pycache__, .venv, build, dist
- Manual execution: `black .` and `isort .`

**Risks & Mitigations:**
- File lock on DuckDB: avoid concurrent writers; schedule syncs
- Sync latency: adjust Airbyte schedule; use incremental
- Data drift: Soda gates + dbt tests + freshness checks
- Code inconsistency: Black + isort enforcement
- API inconsistency: ⚠️ API uses SQL Server while pipeline uses PostgreSQL

**Development Patterns (Without Makefile):**
```bash
# Environment setup
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# Development workflow
docker-compose up -d db  # Start PostgreSQL
python -m uvicorn api.main:app --reload  # Start API

# Code quality
black .  # Format code
isort .  # Sort imports

# Production workflow
python run_spider.py --spider all --keyword "IT"
python PyAirbyte/airbyte.py  # Sync to DuckDB
```