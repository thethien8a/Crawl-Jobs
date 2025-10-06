# Data Warehouse Architecture - CrawlJob

## Overview
CrawlJob uses **Kimball Dimensional Modeling** with **Bronze-Silver-Gold (Medallion) Architecture** implemented in DuckDB.

## Architecture Layers

### Bronze Layer (Raw)
- **bronze.jobs**: Exact replica from PostgreSQL sync
- Purpose: Archive, enable reprocessing
- Loading: Incremental MERGE via `sync_pg_to_duck/sync.py`

### Silver Layer (Cleaned & Normalized)
- **silver.stg_jobs**: Cleaned, validated, normalized jobs
- Transformations: Text cleaning, salary parsing, skill extraction, standardization
- Loading: Incremental dbt model
- Quality: dbt tests for validation

### Gold Layer (Analytics-Ready - Star Schema)

#### Fact Tables
1. **fct_jobs** (Core fact)
   - Grain: One row per job posting
   - Keys: company_sk, location_sk, industry_sk, job_category_sk, source_site_sk, scraped_date_sk, deadline_date_sk
   - Measures: salary_min, salary_max, salary_avg
   - Flags: has_salary, is_remote, is_urgent, is_active

2. **fct_job_skills** (Bridge table)
   - Grain: One row per job-skill relationship
   - Keys: job_sk, skill_sk
   - Attributes: skill_level, is_required, years_required

3. **fct_daily_job_stats** (Aggregate fact)
   - Grain: Daily snapshot by dimensions
   - Metrics: total_jobs, new_jobs, expired_jobs, avg_salary, median_salary
   - Purpose: Pre-aggregated for dashboard performance

#### Dimension Tables

1. **dim_company** (SCD Type 2)
   - Business Key: company_name_raw
   - Attributes: company_name, company_size, company_type, industry, headquarters
   - SCD Tracking: effective_date, expiration_date, is_current, version_number
   - Purpose: Track company evolution (size changes, relocations, etc.)

2. **dim_location** (Type 0)
   - Hierarchy: country → region → city → district → ward
   - Attributes: is_major_city, latitude, longitude
   - Purpose: Geographic analysis with drill-down

3. **dim_industry** (Type 0)
   - Hierarchy: industry_l1 → industry_l2 → industry_l3
   - Attributes: industry_code (NAICS/VSIC), description
   - Purpose: Industry classification

4. **dim_job_category** (Type 0)
   - Hierarchy: category_l1 → category_l2 → category_l3
   - Attributes: seniority_level, job_type, experience_years, education_level
   - Purpose: Job classification and seniority

5. **dim_skill** (SCD Type 3)
   - Business Key: skill_name
   - Current: popularity_score, demand_trend
   - Previous: previous_popularity_score, previous_score_date, score_change_pct
   - Purpose: Track skill trends (current vs previous month)

6. **dim_source_site** (SCD Type 1)
   - Business Key: source_name
   - Attributes: source_url, avg_data_quality, crawl_success_rate
   - Purpose: Job board metadata (overwrite, no history needed)

7. **dim_date** (Type 0)
   - Standard date dimension (2020-2029)
   - Attributes: year, quarter, month, week, day hierarchies
   - Flags: is_weekend, is_holiday, is_working_day, is_current_month, etc.

## SCD Strategy

| Dimension | SCD Type | Rationale |
|-----------|----------|-----------|
| dim_date | Type 0 | Calendar is immutable |
| dim_location | Type 0 | Cities rarely change |
| dim_industry | Type 0 | Static taxonomy |
| dim_job_category | Type 0 | Standard classification |
| dim_source_site | Type 1 | No history needed for metrics |
| dim_company | Type 2 | Track company growth/changes |
| dim_skill | Type 3 | Current + previous month trend |

## Data Flow
```
Scrapy → PostgreSQL (raw)
  ↓
Soda Core (quality gates)
  ↓
sync_pg_to_duck/sync.py (MERGE to bronze.jobs)
  ↓
dbt: bronze → silver (stg_jobs)
  ↓
dbt: silver → gold (dimensions + facts)
  ↓
Superset (BI) + FastAPI (serving)
```

## Key Analytical Use Cases
1. **Salary Benchmarking**: By job category, seniority, location
2. **Skills Demand**: Top skills, skill combinations, trending skills
3. **Company Hiring Trends**: Jobs posted over time, with historical context
4. **Regional Market Analysis**: Jobs by city/region/industry
5. **Time Series Trends**: Daily/monthly job posting patterns
6. **Company Evolution**: Track changes via SCD Type 2

## Performance Optimizations
- Indexes on FK columns (company_sk, location_sk, date_sk)
- Pre-aggregated facts (fct_daily_job_stats)
- Materialized views (optional for common queries)
- Partitioning by date (future improvement)

## Documentation
- Full architecture: `document/plan/DATA_WAREHOUSE_ARCHITECTURE.md`
- SCD guide: `document/learning/data-warehouse-scd-guide.md`
- Documentation index: `document/README.md`

## dbt Project Structure
```
dbt_crawjob/models/
├── bronze/
│   └── schema.yml
├── silver/
│   ├── stg_jobs.sql (incremental)
│   └── schema.yml
└── gold/
    ├── dim_company.sql (SCD Type 2)
    ├── dim_location.sql
    ├── dim_industry.sql
    ├── dim_job_category.sql
    ├── dim_skill.sql (SCD Type 3)
    ├── dim_source_site.sql (SCD Type 1)
    ├── dim_date.sql
    ├── fct_jobs.sql (incremental)
    ├── fct_job_skills.sql (incremental)
    ├── fct_daily_job_stats.sql (daily aggregation)
    └── schema.yml (with tests)
```

## Next Steps for Implementation
1. Generate dim_date seed data
2. Implement SCD Type 2 for dim_company (use dbt snapshots or manual logic)
3. Implement SCD Type 3 for dim_skill
4. Create incremental fact tables
5. Add comprehensive dbt tests
6. Integrate into Airflow DAG
7. Connect Superset to Gold schema
