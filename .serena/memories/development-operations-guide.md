# CrawlJob - Development Operations Guide

## Project Setup

### Directory Structure
```
CrawlJob/
├── CrawlJob/                    # Scrapy project
│   ├── spiders/                 # Spider files
│   ├── items.py                 # Item definitions
│   ├── pipelines.py             # Data pipelines
│   ├── settings.py              # Scrapy settings
│   └── selenium_middleware.py   # Selenium middleware
├── dbt_crawjob/                 # dbt project
│   ├── models/
│   │   ├── sources.yml          # Source definitions
│   │   ├── silver/
│   │   │   ├── stg_jobs.sql    # Main staging model
│   │   │   ├── schema.yml      # Tests & docs
│   │   │   └── README.md
│   │   └── gold/               # Future
│   ├── macros/                  # Reusable macros
│   ├── analyses/                # Ad-hoc queries
│   ├── tests/                   # Data tests
│   ├── dbt_project.yml         # dbt config
│   └── profiles.yml            # DB connections
├── airflow/                     # Orchestration
│   └── dags/
│       └── crawljob_pipeline.py
├── DuckDB/
│   └── warehouse.duckdb        # Analytics DB
├── logs/                        # Execution logs
├── outputs/                     # Scraped data
├── requirements.txt            # Python deps
└── README.md
```

## Development Workflow

### 1. Data Collection (Scrapy)

**Run single spider:**
```bash
cd d:\Practice\Scrapy\CrawlJob
scrapy crawl joboko -a keyword="python developer"
```

**Run all spiders:**
```bash
python run_spider.py
```

**Output**:
- PostgreSQL: `bronze.jobs` table
- JSON files: `outputs/jobs_YYYY-MM-DD_HH-MM-SS.json`
- Logs: `logs/crawl_YYYY-MM-DD_HH-MM-SS.log`

### 2. Data Transformation (dbt)

**Setup Python environment:**
```bash
cd d:\Practice\Scrapy\CrawlJob\dbt_crawjob

# First time only
python -m venv .venv
.venv\Scripts\activate
pip install dbt-core dbt-postgres dbt-duckdb
```

**Build models:**
```bash
# Build all models
dbt run

# Build specific model
dbt run --select stg_jobs

# Full refresh (rebuild from scratch)
dbt run --select stg_jobs --full-refresh
```

**Run tests:**
```bash
# Test all
dbt test

# Test specific model
dbt test --select stg_jobs

# Test specific test
dbt test --select stg_jobs --select test_name:unique
```

**Generate documentation:**
```bash
dbt docs generate
dbt docs serve  # Opens browser at localhost:8080
```

**Compile SQL (for debugging):**
```bash
dbt compile --select stg_jobs
# Check: target/compiled/crawljob/models/silver/stg_jobs.sql
```

### 3. Quality Checks

**Run quality queries:**
```bash
cd dbt_crawjob
dbt compile --select staging_data_quality

# Copy SQL from target/compiled/crawljob/analyses/staging_data_quality.sql
# Run in DuckDB or PostgreSQL client
```

**Check data:**
```bash
# Show sample data
dbt show --select stg_jobs --limit 10

# Profile data
dbt run-operation generate_model_yaml --args '{model_name: stg_jobs}'
```

### 4. Debugging

**Debug dbt model:**
```bash
# Enable debug logging
dbt run --select stg_jobs --debug

# Verbose output
dbt run --select stg_jobs --log-level debug
```

**Check compiled SQL:**
```bash
dbt compile --select stg_jobs
cat target/compiled/crawljob/models/silver/stg_jobs.sql
```

**Test in database directly:**
```sql
-- Connect to DuckDB
duckdb DuckDB/warehouse.duckdb

-- Run compiled SQL
.read target/compiled/crawljob/models/silver/stg_jobs.sql
```

## Database Connections

### PostgreSQL (Bronze)

**Connection String** (in `profiles.yml`):
```yaml
crawljob:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      port: 5432
      user: postgres
      password: <password>
      database: crawljob
      schema: bronze
```

**Direct Connection:**
```bash
psql -U postgres -d crawljob
```

**Check data:**
```sql
SELECT COUNT(*), source_site 
FROM bronze.jobs 
GROUP BY source_site;
```

### DuckDB (Silver/Gold)

**Connection String** (in `profiles.yml`):
```yaml
crawljob:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: DuckDB/warehouse.duckdb
      schema: silver
```

**Direct Connection:**
```bash
duckdb DuckDB/warehouse.duckdb
```

**Check data:**
```sql
SELECT COUNT(*), source_name 
FROM silver.stg_jobs 
GROUP BY source_name;
```

## Common Tasks

### Task 1: Add New Source

**Step 1: Create spider**
```bash
cd CrawlJob
# Create new spider file: spiders/newsource_spider.py
```

**Step 2: Add to dbt model**
```sql
-- Edit: dbt_crawjob/models/silver/stg_jobs.sql

-- Add CASE WHEN for salary (line ~100)
when source_site = 'newsource.com' then
  case
    when lower(salary_raw) like '%pattern%' then 'Normalized'
    else trim(salary_raw)
  end

-- Add source_name mapping (line ~200)
when source_site = 'newsource.com' then 'newsource'
```

**Step 3: Update schema.yml**
```yaml
# Add to accepted_values in source_name column
- 'newsource'
```

**Step 4: Test**
```bash
# Run spider
scrapy crawl newsource -a keyword="test"

# Build dbt
dbt run --select stg_jobs

# Test
dbt test --select stg_jobs
```

### Task 2: Update Normalization Logic

**Scenario**: JobOKO thay đổi salary format

**Step 1: Edit stg_jobs.sql**
```sql
-- Find JobOKO salary section (line ~90)
when source_site = 'vn.joboko.com' then
  case
    when lower(salary_raw) like '%new_pattern%' then 'New Value'  -- ADD THIS
    when lower(salary_raw) like '%thỏa thuận%' then 'Negotiable'
    else trim(salary_raw)
  end
```

**Step 2: Test**
```bash
dbt run --select stg_jobs --full-refresh
dbt test --select stg_jobs
```

**Step 3: Verify**
```sql
-- Check normalization
SELECT source_name, salary, COUNT(*)
FROM silver.stg_jobs
WHERE source_name = 'joboko'
GROUP BY source_name, salary;
```

### Task 3: Troubleshoot Failed Tests

**Scenario**: `test_not_null_job_title` fails

**Step 1: Identify issue**
```bash
dbt test --select stg_jobs --select test_name:not_null_job_title
# Error: Found 5 rows with NULL job_title
```

**Step 2: Investigate**
```sql
-- Find NULL rows
SELECT source_name, job_url, job_title
FROM silver.stg_jobs
WHERE job_title IS NULL;
```

**Step 3: Fix**
```sql
-- Option A: Fix in stg_jobs.sql (filter out)
WHERE job_title IS NOT NULL

-- Option B: Fix at source (spider)
# Edit spider to skip jobs without title

-- Option C: Set severity to warn
# In schema.yml:
tests:
  - not_null:
      severity: warn
```

### Task 4: Monitor Data Quality

**Daily Check:**
```bash
cd dbt_crawjob
dbt compile --select staging_data_quality

# Run queries 1-4 in staging_data_quality.sql
# Check for:
# - Row count drop
# - Missing sources
# - Low completeness
```

**Weekly Check:**
```bash
# Run all quality queries
# Check trends:
# - Salary normalization consistency
# - Experience distribution changes
# - New quality issues
```

### Task 5: Performance Optimization

**Check execution time:**
```bash
dbt run --select stg_jobs --log-level info
# Look for: "Completed in 10.5s"
```

**Profile query:**
```sql
-- In DuckDB
EXPLAIN ANALYZE 
SELECT * FROM silver.stg_jobs;
```

**Optimize:**
```sql
-- Add indexes in bronze
CREATE INDEX idx_scraped_at ON bronze.jobs(scraped_at);
CREATE INDEX idx_source_site ON bronze.jobs(source_site);

-- Partition by date (future)
```

## Git Workflow

### Branching Strategy

```
main (production)
└── dbt (development) ← current branch
    ├── feature/new-source
    ├── feature/gold-layer
    └── fix/data-quality
```

### Commit Conventions

```bash
# Feature
git commit -m "feat(silver): add Glints source normalization"

# Fix
git commit -m "fix(silver): correct JobOKO salary pattern"

# Refactor
git commit -m "refactor(silver): migrate to hybrid approach"

# Docs
git commit -m "docs(silver): update README with examples"

# Test
git commit -m "test(silver): add completeness tests"
```

### Typical Workflow

```bash
# 1. Pull latest
git pull origin dbt

# 2. Make changes
# ... edit files ...

# 3. Test locally
dbt run --select stg_jobs
dbt test --select stg_jobs

# 4. Commit
git add .
git commit -m "feat(silver): add new normalization logic"

# 5. Push
git push origin dbt
```

## Environment Management

### Development (.env.dev)
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=crawljob_dev
```

### Production (.env.prod)
```
DB_HOST=prod-server
DB_PORT=5432
DB_NAME=crawljob_prod
```

### Switching Environments
```bash
# Use different profiles
dbt run --target dev
dbt run --target prod
```

## Monitoring & Alerting (Future)

### Metrics to Track
1. Spider success rate
2. Row counts per source
3. Data freshness (last scrape time)
4. Field completeness %
5. Test pass rate
6. Build duration

### Alerts
- No data scraped in 24h
- Test failures
- Field completeness < 80%
- Build time > 2x normal

## Backup & Recovery

### Backup Strategy
```bash
# PostgreSQL backup
pg_dump -U postgres crawljob > backup_$(date +%Y%m%d).sql

# DuckDB backup
cp DuckDB/warehouse.duckdb DuckDB/backup_$(date +%Y%m%d).duckdb
```

### Recovery
```bash
# Restore PostgreSQL
psql -U postgres crawljob < backup_20251006.sql

# Restore DuckDB
cp DuckDB/backup_20251006.duckdb DuckDB/warehouse.duckdb
```

## Troubleshooting Guide

### Issue: dbt build fails

**Error**: "Database connection failed"
**Solution**:
```bash
# Check profiles.yml
cat profiles.yml

# Test connection
dbt debug
```

**Error**: "Model stg_jobs not found"
**Solution**:
```bash
# Check model name in schema.yml matches file name
# Ensure no typos
```

### Issue: Tests fail after adding source

**Error**: "accepted_values test failed for source_name"
**Solution**:
```yaml
# Update schema.yml accepted_values list
- name: source_name
  tests:
    - accepted_values:
        values: ['joboko', 'topcv', 'vietnamworks', 'newsource']
```

### Issue: Incremental not working

**Symptom**: Every run rebuilds entire table
**Solution**:
```sql
-- Check incremental config
{{ config(materialized='incremental') }}

-- Check incremental logic
{% if is_incremental() %}
    WHERE scraped_at > (SELECT MAX(scraped_at) FROM {{ this }})
{% endif %}

-- Force full refresh
dbt run --select stg_jobs --full-refresh
```

## IDE Setup (VS Code)

### Recommended Extensions
- `innoverio.vscode-dbt-power-user` - dbt Power User
- `ms-python.python` - Python
- `mtxr.sqltools` - SQL Tools
- `evidence-dev.sqltools-duckdb-driver` - DuckDB driver

### Workspace Settings
```json
{
  "dbt.projectRoot": "dbt_crawjob",
  "python.defaultInterpreterPath": "dbt_crawjob/.venv/Scripts/python.exe",
  "sqltools.connections": [
    {
      "name": "DuckDB",
      "driver": "DuckDB",
      "database": "DuckDB/warehouse.duckdb"
    }
  ]
}
```

## Performance Benchmarks

### Current Performance (Oct 2025)

| Operation | Time | Notes |
|-----------|------|-------|
| Spider run (1 source) | ~2 min | 100 jobs |
| dbt run (stg_jobs) | ~10s | Incremental |
| dbt test (stg_jobs) | ~5s | All tests |
| Full refresh | ~30s | All data |

### Target Performance

| Operation | Target | Strategy |
|-----------|--------|----------|
| Spider run | <1 min | Async requests |
| dbt run | <5s | Better indexing |
| dbt test | <3s | Parallel execution |

## Reference Commands

### Scrapy
```bash
scrapy crawl <spider_name> -a keyword="<keyword>"
scrapy list  # List all spiders
scrapy check  # Check spider code
```

### dbt
```bash
dbt run --select <model>
dbt test --select <model>
dbt docs generate
dbt docs serve
dbt compile --select <model>
dbt show --select <model> --limit <n>
dbt debug  # Check setup
dbt clean  # Clean target/ folder
```

### DuckDB
```bash
duckdb <database>
.tables  # List tables
.schema <table>  # Show schema
.mode line  # Change output format
```

### Git
```bash
git status
git add .
git commit -m "<message>"
git push origin <branch>
git pull origin <branch>
```
