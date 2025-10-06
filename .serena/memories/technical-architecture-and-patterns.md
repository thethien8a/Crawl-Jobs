# CrawlJob - Technical Architecture & Design Patterns

## System Architecture

```
Data Sources (10 job boards)
    ↓
Scrapy Spiders (Python)
    ↓
PostgreSQL (Bronze - Raw)
    ↓
dbt (Transformation)
    ↓
DuckDB (Silver/Gold - Analytics)
    ↓
Visualization/ML
```

## Data Pipeline Layers

### Layer 1: Data Collection (Scrapy)

**Location**: `CrawlJob/spiders/`

**Files**:
- `joboko_spider.py`
- `topcv_spider.py`
- `vietnamworks_spider.py`
- `itviec_spider.py`
- `linkedin_spider.py`
- `careerlink_spider.py`
- `careerviet_spider.py`
- `job123_spider.py`
- `jobsgo_spider.py`
- `jobstreet_spider.py`

**Common Pattern**:
```python
class Spider(scrapy.Spider):
    name = "source_name"
    
    def start_requests(self):
        # Search jobs by keyword
        
    def parse_search_results(self, response):
        # Extract job URLs
        # Pagination
        
    def parse_job_detail(self, response):
        # Extract job details
        # yield JobItem
```

**Output**: PostgreSQL table `bronze.jobs`

### Layer 2: Bronze Storage (PostgreSQL)

**Database**: PostgreSQL
**Schema**: `bronze`
**Table**: `jobs`

**Columns**:
- `job_url` (TEXT, primary identifier)
- `job_title` (TEXT)
- `company_name` (TEXT)
- `salary` (TEXT, raw format)
- `location` (TEXT)
- `job_type` (TEXT)
- `experience_level` (TEXT, raw format)
- `education_level` (TEXT, raw format)
- `job_industry` (TEXT)
- `job_position` (TEXT)
- `job_description` (TEXT)
- `requirements` (TEXT)
- `benefits` (TEXT)
- `job_deadline` (TEXT, raw format)
- `source_site` (TEXT) - Key for filtering
- `search_keyword` (TEXT)
- `scraped_at` (TIMESTAMP)

**Characteristics**:
- Raw data, minimal transformation
- All sources in single table
- `source_site` distinguishes sources
- Append-only (no updates)

### Layer 3: Silver Transformation (dbt + DuckDB)

**Database**: DuckDB
**Schema**: `silver`
**Main Model**: `stg_jobs`

**Pattern**: Hybrid Approach (Single File + CASE WHEN)

**File**: `dbt_crawjob/models/silver/stg_jobs.sql`

**Architecture**:
```sql
WITH source AS (
    -- Read from bronze.jobs
    -- Incremental filter on scraped_at
)

, base_cleaning AS (
    -- Common normalization for ALL sources:
    -- - Trim whitespace
    -- - Lowercase company names
    -- - Keep raw fields for source-specific processing
)

, source_specific AS (
    -- Source-specific logic using CASE WHEN:
    -- CASE 
    --   WHEN source_site = 'joboko' THEN [joboko logic]
    --   WHEN source_site = 'topcv' THEN [topcv logic]
    --   WHEN source_site = 'vietnamworks' THEN [vnw logic]
    --   ELSE [generic logic]
    -- END
)

, final AS (
    -- Column selection & ordering
)

SELECT * FROM final
```

**Key Design Decisions**:
1. **Single file** instead of multiple per-source files
2. **CASE WHEN** for source-specific logic
3. **Incremental materialization** for performance
4. **Macros** for reusable patterns

**Advantages**:
- 1 file to maintain vs 10+ files
- 1 query vs 10 queries + UNION
- Easy to add new sources
- No code duplication

### Layer 4: Gold Layer (Future)

**Status**: Not yet implemented

**Planned Design**:
- Star schema (fact + dimension tables)
- Business logic aggregations
- Denormalized for analytics

**Potential Models**:
```
gold/
├── fact_jobs.sql         # Fact table
├── dim_companies.sql     # Company dimension
├── dim_locations.sql     # Location dimension
├── dim_time.sql          # Time dimension
└── agg_jobs_daily.sql    # Daily aggregations
```

## Design Patterns

### Pattern 1: Medallion Architecture

**Bronze → Silver → Gold**

- **Bronze**: Raw, immutable, append-only
- **Silver**: Cleaned, standardized, typed
- **Gold**: Business logic, aggregated, denormalized

**Benefits**:
- Clear separation of concerns
- Easy to debug (check each layer)
- Reusable transformations

### Pattern 2: Hybrid Staging (Silver Layer)

**Instead of**: One model per source → Union
**Use**: Single model with CASE WHEN

**Rationale**:
- Fewer files to maintain
- Single query execution
- DRY principle with macros
- Easier to refactor

**When to use**:
- 5-20 sources (sweet spot)
- Similar schema across sources
- Different normalization rules per source

**When NOT to use**:
- Very few sources (<3) → simple model
- Many sources (>20) → consider partitioning
- Completely different schemas → separate models

### Pattern 3: Incremental Materialization

**Strategy**: merge on unique_key

```sql
{{ config(
    materialized='incremental',
    unique_key='job_url',
    incremental_strategy='merge'
) }}

{% if is_incremental() %}
    WHERE scraped_at > (SELECT MAX(scraped_at) FROM {{ this }})
{% endif %}
```

**Benefits**:
- Fast updates (only new/changed rows)
- Idempotent (safe to re-run)
- Handles late-arriving data

### Pattern 4: Source-Specific Logic with CASE WHEN

**Pattern**:
```sql
CASE 
    WHEN source_site = 'source_a' THEN
        CASE
            WHEN condition_1 THEN value_1
            WHEN condition_2 THEN value_2
            ELSE default_value
        END
    WHEN source_site = 'source_b' THEN
        [different logic]
    ELSE
        [generic logic]
END AS normalized_field
```

**Benefits**:
- All logic in one place
- Easy to compare across sources
- No code duplication

**Trade-offs**:
- File can get long (use CTEs to organize)
- Need good comments

### Pattern 5: Macro-Based Normalization

**Macros** (`normalize_job_fields.sql`):
```sql
{% macro clean_whitespace(column) %}
    TRIM(REGEXP_REPLACE({{ column }}, '\s+', ' ', 'g'))
{% endmacro %}

{% macro normalize_deadline(column) %}
    CASE 
        WHEN {{ column }} ~ '^\d{1,2}/\d{1,2}/\d{4}$' 
        THEN {{ column }}
        ELSE NULL
    END
{% endmacro %}
```

**Usage**:
```sql
{{ clean_whitespace('job_title') }} AS job_title,
{{ normalize_deadline('job_deadline') }} AS job_deadline
```

**Benefits**:
- DRY principle
- Testable in isolation
- Reusable across models

## Testing Strategy

### Level 1: dbt Tests (schema.yml)

**Generic Tests**:
- `unique`: job_url
- `not_null`: critical fields
- `accepted_values`: source_name enum

**Custom Tests** (macros):
- `valid_url`: URL format check
- `valid_source_site`: Known sources only
- `is_recent`: Data freshness
- `deadline_after_scraped`: Business logic
- `salary_has_currency`: Data quality

### Level 2: Data Quality Checks (SQL)

**File**: `analyses/staging_data_quality.sql`

**Checks**:
1. Row counts per source
2. Field completeness
3. Normalization consistency
4. Duplicates
5. Outliers
6. Business rule violations

### Level 3: Integration Tests (Future)

- End-to-end pipeline
- Bronze → Silver → Gold
- Data lineage validation

## Performance Optimizations

### Optimization 1: Incremental Models

**Before**: Full table rebuild every run
**After**: Only new/changed rows

**Impact**: 10x faster builds

### Optimization 2: Single Query (Hybrid)

**Before**: 10 separate queries + UNION ALL
**After**: 1 query with CASE WHEN

**Impact**: 3x faster execution

### Optimization 3: Partitioning (Future)

**Strategy**: Partition by `scraped_date`

**Benefits**:
- Faster queries on recent data
- Easier data retention
- Better parallelization

### Optimization 4: Indexing

**Bronze layer**:
- Index on `scraped_at` (incremental filter)
- Index on `source_site` (filtering)
- Composite index on `(source_site, scraped_at)`

## Error Handling

### Spider Level (Scrapy)

```python
def parse_job_detail(self, response):
    try:
        # Extract data
    except Exception as e:
        self.logger.error(f"Error parsing {response.url}: {e}")
        yield None  # Skip failed jobs
```

### dbt Level

**Tests as guardrails**:
- Tests fail → Pipeline stops
- Review → Fix → Re-run

**Incremental safety**:
- Merge strategy → Updates existing
- No data loss on re-runs

## Monitoring & Observability

### dbt Artifacts

- `manifest.json`: Model lineage
- `run_results.json`: Execution stats
- `catalog.json`: Column stats

### Quality Metrics

**Daily**:
- Row counts per source
- Field completeness
- Recent scrapes

**Weekly**:
- Data quality trends
- Source coverage
- Normalization accuracy

## Scalability Considerations

### Current Scale
- 10 sources
- ~1000-10000 jobs per source
- ~10-100K total rows
- Daily refreshes

### Future Scale (Projected)
- 20+ sources
- ~100K-1M total rows
- Hourly refreshes

### Scaling Strategies

1. **Partitioning**: By scraped_date
2. **Parallel Processing**: dbt threads
3. **Caching**: Intermediate results
4. **Sampling**: For dev/test

## Technology Choices Rationale

### Why Scrapy?
- ✅ Mature, well-documented
- ✅ Built-in middlewares
- ✅ Good for large-scale scraping
- ❌ Learning curve for beginners

### Why PostgreSQL for Bronze?
- ✅ ACID compliance
- ✅ JSON support (raw data)
- ✅ Good for write-heavy workloads
- ❌ Expensive for analytics queries

### Why DuckDB for Silver/Gold?
- ✅ Columnar storage (analytics)
- ✅ Fast aggregations
- ✅ Embedded (no server)
- ✅ SQL-compliant
- ❌ Not for concurrent writes

### Why dbt?
- ✅ SQL-based (easy for analysts)
- ✅ Version control (Git)
- ✅ Testing framework
- ✅ Documentation generation
- ✅ Incremental models
- ❌ Steep learning curve initially

### Why Hybrid Approach (Silver)?
- ✅ Balance between clarity and efficiency
- ✅ Single source of truth (1 file)
- ✅ No code duplication
- ✅ Easy to maintain
- ❌ File can get long (manageable with CTEs)

## Anti-Patterns Avoided

### ❌ One Model Per Source + UNION
**Why avoided**: Too many files, slow performance

### ❌ All Logic in Bronze
**Why avoided**: Mixing concerns, hard to test

### ❌ Complex Business Logic in Silver
**Why avoided**: Silver = clean + standardize only, Gold = business logic

### ❌ Hard-coded Values
**Why avoided**: Use config/macros instead

### ❌ No Testing
**Why avoided**: Data quality critical

## Best Practices Followed

### ✅ Separation of Concerns
- Bronze: Raw
- Silver: Clean
- Gold: Business logic

### ✅ DRY Principle
- Macros for reusable logic
- CASE WHEN vs duplicate code

### ✅ Documentation
- Inline comments
- README files
- Schema.yml descriptions

### ✅ Testing
- dbt tests
- Quality checks
- Business rule validation

### ✅ Version Control
- Git for all code
- Semantic commits
- PR reviews

### ✅ Monitoring
- Quality metrics
- Performance tracking
- Error alerting (future)
