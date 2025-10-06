# 📚 **SCD (Slowly Changing Dimensions) - Complete Guide**

## 📋 **Table of Contents**

1. [What is SCD?](#what-is-scd)
2. [When to Use SCD?](#when-to-use-scd)
3. [SCD Types Overview](#scd-types-overview)
4. [Type 0: No Change](#type-0-no-change)
5. [Type 1: Overwrite](#type-1-overwrite)
6. [Type 2: Add New Row](#type-2-add-new-row)
7. [Type 3: Add New Column](#type-3-add-new-column)
8. [Type 4: Mini-Dimension](#type-4-mini-dimension)
9. [Type 6: Hybrid](#type-6-hybrid)
10. [CrawlJob Implementation](#crawljob-implementation)
11. [dbt Implementation](#dbt-implementation)

---

## 🎯 **What is SCD?**

**Slowly Changing Dimensions (SCD)** là các kỹ thuật để xử lý **sự thay đổi dữ liệu trong dimension tables** của data warehouse.

### **Key Concepts**

- **Dimension Tables**: Chứa descriptive attributes (Company, Location, Product, etc.)
- **Slowly Changing**: Attributes thay đổi **không thường xuyên** (khác với fact tables)
- **Historical Tracking**: Quyết định có lưu lịch sử thay đổi hay không

### **Why SCD Matters?**

✅ **Accuracy**: Phản ánh đúng historical context  
✅ **Compliance**: Audit trail cho legal requirements  
✅ **Analytics**: Time-based analysis (trends, comparisons)  
✅ **Business Logic**: Decision-making dựa trên historical data

---

## 📊 **When to Use SCD?**

### **SCD Applies To:**
- ✅ **Dimension Tables** (dim_company, dim_product, dim_customer)
- ✅ Attributes that change **slowly** (address, category, status)
- ✅ When **historical context matters** for analysis

### **SCD Does NOT Apply To:**
- ❌ **Fact Tables** (transactions are immutable)
- ❌ **Bridge Tables** (relationship tables)
- ❌ **Aggregate Tables** (recalculated from source)
- ❌ Attributes that change **very frequently** (use mini-dimensions instead)

---

## 🗂️ **SCD Types Overview**

| Type | Name | History | Storage | Complexity | Use Case |
|------|------|---------|---------|------------|----------|
| **0** | No Change | ❌ None | ⭐ Minimal | ⭐ Simplest | Static reference data |
| **1** | Overwrite | ❌ None | ⭐ Minimal | ⭐ Simple | Error corrections |
| **2** | Add Row | ✅ Full | ⭐⭐⭐ High | ⭐⭐⭐ Complex | Full audit trail |
| **3** | Add Column | ⚠️ Limited | ⭐⭐ Medium | ⭐⭐ Medium | Previous value only |
| **4** | Mini-Dimension | ✅ Separate | ⭐⭐ Medium | ⭐⭐⭐ Complex | Rapidly changing attrs |
| **6** | Hybrid (1+2+3) | ✅ Partial | ⭐⭐⭐ High | ⭐⭐⭐ Very Complex | Mixed requirements |

---

## ❄️ **SCD Type 0: No Change Tracking**

### **Concept**
Dữ liệu **không bao giờ thay đổi** sau khi insert. Immutable.

### **When to Use**
- ✅ Static reference data (Countries, Provinces)
- ✅ Historical facts (Date of birth, Registration date)
- ✅ Fixed taxonomies (Industry codes)
- ✅ Calendar dimensions (Date dimension)

### **Schema**
```sql
CREATE TABLE dim_location (
    location_sk     BIGINT PRIMARY KEY,
    city            VARCHAR NOT NULL,
    region          VARCHAR NOT NULL,
    country         VARCHAR NOT NULL,  -- Always 'Vietnam'
    latitude        DECIMAL(10,6),
    longitude       DECIMAL(10,6),
    
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Example**
```sql
-- Insert once, never update
INSERT INTO dim_location VALUES
(1, 'Hà Nội', 'North', 'Vietnam', 21.0285, 105.8542, CURRENT_TIMESTAMP);

-- This would be an ERROR (violates Type 0 principle)
UPDATE dim_location SET city = 'Hanoi' WHERE location_sk = 1;  -- ❌ DON'T DO THIS
```

### **Pros & Cons**
✅ Simplest to implement  
✅ Minimal storage  
✅ Fastest queries  
❌ Cannot handle changes  
❌ No flexibility  

### **CrawlJob Examples**
```sql
-- dim_date (Calendar never changes)
-- dim_location (Vietnamese cities/provinces are stable)
-- dim_industry (Standard industry taxonomy)
```

---

## 🔄 **SCD Type 1: Overwrite**

### **Concept**
**Ghi đè** dữ liệu cũ bằng dữ liệu mới. **KHÔNG giữ history**.

### **When to Use**
- ✅ Correcting errors (typos, wrong data)
- ✅ Attributes không cần historical context
- ✅ Storage/performance is critical
- ✅ Latest value is all that matters

### **Schema**
```sql
CREATE TABLE dim_source_site (
    source_site_sk      BIGINT PRIMARY KEY,
    source_name         VARCHAR UNIQUE NOT NULL,
    source_url          VARCHAR,              -- Can be updated
    avg_data_quality    DECIMAL(3,2),         -- Updated frequently
    crawl_success_rate  DECIMAL(3,2),         -- Updated frequently
    
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Track last update
);
```

### **Update Process**
```sql
-- Initial insert
INSERT INTO dim_source_site VALUES
(1, 'itviec', 'https://itviec.com', 0.95, 0.98, NOW(), NOW());

-- Type 1 Update: Overwrite (e.g., URL changed)
UPDATE dim_source_site 
SET source_url = 'https://itviec.com/vi',
    updated_at = NOW()
WHERE source_name = 'itviec';

-- Result: Only 1 row, old URL is LOST
SELECT * FROM dim_source_site WHERE source_name = 'itviec';
-- (1, 'itviec', 'https://itviec.com/vi', 0.95, 0.98, ..., NOW())
```

### **dbt Implementation**
```sql
-- models/gold/dim_source_site.sql
{{
  config(
    materialized='table',
    unique_key='source_name'
  )
}}

SELECT
    ROW_NUMBER() OVER (ORDER BY source_name) AS source_site_sk,
    source_name,
    source_url,
    avg_data_quality,
    crawl_success_rate,
    CURRENT_TIMESTAMP AS created_at,
    CURRENT_TIMESTAMP AS updated_at
FROM {{ ref('stg_source_sites') }}
```

### **Pros & Cons**
✅ Simple to implement  
✅ Minimal storage (1 row per entity)  
✅ Fast queries  
✅ No join complexity  
❌ **LOSE HISTORY** (biggest drawback)  
❌ Cannot do time-based analysis  
❌ No audit trail  

### **CrawlJob Examples**
```sql
-- dim_source_site (Website metadata doesn't need history)
-- avg_data_quality, crawl_success_rate are overwritten daily
```

---

## 📜 **SCD Type 2: Add New Row** ⭐ (Most Common)

### **Concept**
Thêm **row mới** cho mỗi thay đổi. Giữ **toàn bộ history**.

### **When to Use**
- ✅ **Historical tracking is critical** (most common use case)
- ✅ Compliance/audit requirements
- ✅ Time-based analysis needed
- ✅ Business logic depends on historical context

### **Schema**
```sql
CREATE TABLE dim_company (
    -- Surrogate Key (auto-increment, unique for each row)
    company_sk          BIGINT PRIMARY KEY,
    
    -- Business Key (natural key, can have duplicates)
    company_name_raw    VARCHAR NOT NULL,
    
    -- Attributes (can change over time)
    company_name        VARCHAR NOT NULL,
    company_size        VARCHAR,              -- Can change: '201-500' → '500+'
    company_type        VARCHAR,
    industry            VARCHAR,
    headquarters        VARCHAR,              -- Can relocate
    
    -- SCD Type 2 Tracking Columns
    effective_date      DATE NOT NULL,        -- When this version became active
    expiration_date     DATE,                 -- When this version expired (NULL = current)
    is_current          BOOLEAN NOT NULL DEFAULT TRUE,  -- Quick filter for current
    version_number      INTEGER DEFAULT 1,    -- Optional: version counter
    
    -- Audit
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_company_name (company_name),
    INDEX idx_current (is_current),
    INDEX idx_effective_date (effective_date)
);
```

### **Example: Company Growth Over Time**

**Initial State (Jan 2024)**
```sql
INSERT INTO dim_company VALUES
(1, 'FPT Software', 'FPT Software', '201-500', 'MNC', 'IT', 'Hanoi',
 '2024-01-01', NULL, TRUE, 1, NOW(), NOW());
```

| company_sk | company_name | company_size | effective_date | expiration_date | is_current |
|------------|--------------|--------------|----------------|-----------------|------------|
| 1 | FPT Software | 201-500 | 2024-01-01 | NULL | TRUE |

---

**Change Occurs (Jul 2024): Company grows to 500+ employees**

**Step 1**: Close old record
```sql
UPDATE dim_company
SET expiration_date = '2024-06-30',
    is_current = FALSE,
    updated_at = NOW()
WHERE company_sk = 1;
```

**Step 2**: Insert new record
```sql
INSERT INTO dim_company VALUES
(2, 'FPT Software', 'FPT Software', '500+', 'MNC', 'IT', 'Hanoi',  -- Size changed
 '2024-07-01', NULL, TRUE, 2, NOW(), NOW());
```

**Result: 2 rows for same company**

| company_sk | company_name | company_size | effective_date | expiration_date | is_current | version |
|------------|--------------|--------------|----------------|-----------------|------------|---------|
| 1 | FPT Software | 201-500 | 2024-01-01 | 2024-06-30 | FALSE | 1 |
| 2 | FPT Software | 500+ | 2024-07-01 | NULL | TRUE | 2 |

---

### **Querying SCD Type 2**

**1. Get Current Version Only**
```sql
SELECT *
FROM dim_company
WHERE company_name = 'FPT Software'
  AND is_current = TRUE;
  
-- Returns: (2, 'FPT Software', '500+', ...)
```

**2. Get Historical Version (as of specific date)**
```sql
SELECT *
FROM dim_company
WHERE company_name = 'FPT Software'
  AND '2024-03-15' BETWEEN effective_date AND COALESCE(expiration_date, '9999-12-31');
  
-- Returns: (1, 'FPT Software', '201-500', ...)  -- The version valid on March 15, 2024
```

**3. Get All History**
```sql
SELECT 
    company_name,
    company_size,
    effective_date,
    expiration_date,
    version_number
FROM dim_company
WHERE company_name = 'FPT Software'
ORDER BY effective_date;

-- Returns: All 2 versions
```

**4. Join with Fact Table (Point-in-Time Join)**
```sql
-- Jobs posted when FPT was mid-size (201-500 employees)
SELECT 
    f.job_title,
    f.salary_max,
    c.company_size,
    c.effective_date,
    c.expiration_date,
    d.full_date AS job_posted_date
FROM fct_jobs f
JOIN dim_company c ON f.company_sk = c.company_sk
JOIN dim_date d ON f.scraped_date_sk = d.date_sk
WHERE c.company_name = 'FPT Software'
  AND c.company_size = '201-500'
  AND d.full_date BETWEEN c.effective_date AND COALESCE(c.expiration_date, '9999-12-31');
```

---

### **dbt Implementation (Type 2)**

```sql
-- models/gold/dim_company.sql
{{
  config(
    materialized='incremental',
    unique_key='company_sk'
  )
}}

{% set current_date = modules.datetime.date.today() %}

WITH source_data AS (
    SELECT
        company_name,
        company_size,
        company_type,
        industry,
        headquarters
    FROM {{ ref('stg_jobs') }}
    GROUP BY 1, 2, 3, 4, 5
),

existing_current AS (
    SELECT *
    FROM {{ this }}
    WHERE is_current = TRUE
),

changes AS (
    -- Detect changes between source and existing current records
    SELECT
        s.*,
        e.company_sk,
        e.effective_date AS old_effective_date,
        CASE
            WHEN e.company_sk IS NULL THEN 'INSERT'  -- New company
            WHEN s.company_size != e.company_size 
              OR s.headquarters != e.headquarters THEN 'UPDATE'  -- Change detected
            ELSE 'NO_CHANGE'
        END AS change_type
    FROM source_data s
    LEFT JOIN existing_current e ON s.company_name = e.company_name
),

-- Close expired records
close_expired AS (
    SELECT
        company_sk,
        company_name,
        company_size,
        company_type,
        industry,
        headquarters,
        effective_date,
        DATE '{{ current_date }}' - INTERVAL '1 day' AS expiration_date,
        FALSE AS is_current,
        version_number,
        created_at,
        CURRENT_TIMESTAMP AS updated_at
    FROM existing_current e
    WHERE EXISTS (
        SELECT 1 FROM changes c
        WHERE c.company_name = e.company_name
          AND c.change_type = 'UPDATE'
    )
),

-- Insert new records
new_records AS (
    SELECT
        ROW_NUMBER() OVER (ORDER BY company_name) + COALESCE((SELECT MAX(company_sk) FROM {{ this }}), 0) AS company_sk,
        company_name,
        company_size,
        company_type,
        industry,
        headquarters,
        DATE '{{ current_date }}' AS effective_date,
        NULL AS expiration_date,
        TRUE AS is_current,
        COALESCE(e.version_number, 0) + 1 AS version_number,
        CURRENT_TIMESTAMP AS created_at,
        CURRENT_TIMESTAMP AS updated_at
    FROM changes c
    LEFT JOIN existing_current e ON c.company_name = e.company_name
    WHERE c.change_type IN ('INSERT', 'UPDATE')
)

-- Union all parts
SELECT * FROM close_expired
UNION ALL
SELECT * FROM new_records

{% if is_incremental() %}
UNION ALL
SELECT * FROM {{ this }}
WHERE company_sk NOT IN (SELECT company_sk FROM close_expired)
{% endif %}
```

---

### **Pros & Cons**
✅ **Full history** preserved  
✅ Accurate time-based analysis  
✅ Complete audit trail  
✅ Industry standard for DW  
❌ High storage cost (multiple rows per entity)  
❌ Complex queries (need date joins)  
❌ Complex ETL logic  
❌ Slow inserts/updates  

### **CrawlJob Examples**
```sql
-- dim_company (Track company growth, relocations, industry changes)
-- Example: FPT 100 → 500 → 1000 employees over years
```

---

## 🔀 **SCD Type 3: Add New Column**

### **Concept**
Thêm **column mới** để lưu **limited history** (thường 1-2 previous values).

### **When to Use**
- ✅ Only need **current** and **previous** value
- ✅ Space constraints (Type 2 too expensive)
- ✅ Simplified queries (no date joins)
- ✅ Fixed number of historical snapshots

### **Schema**
```sql
CREATE TABLE dim_skill (
    skill_sk                    BIGINT PRIMARY KEY,
    skill_name                  VARCHAR UNIQUE NOT NULL,
    skill_category              VARCHAR,
    
    -- Current values
    popularity_score            INTEGER,            -- Current score
    demand_trend                VARCHAR,            -- Current trend
    
    -- Previous values (Type 3)
    previous_popularity_score   INTEGER,            -- Last month's score
    previous_score_date         DATE,               -- When it was recorded
    score_change_pct            DECIMAL(5,2),       -- % change
    
    -- Metadata
    updated_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Example: Skill Trending**

**Initial State**
```sql
INSERT INTO dim_skill VALUES
(1, 'Python', 'Programming Language', 85, 'Stable', NULL, NULL, NULL, NOW());
```

| skill_name | popularity_score | previous_popularity_score | score_change_pct |
|------------|------------------|---------------------------|------------------|
| Python | 85 | NULL | NULL |

---

**Update (Next Month): Popularity increases**
```sql
UPDATE dim_skill
SET previous_popularity_score = popularity_score,     -- Save current as previous
    previous_score_date = '2024-09-01',
    popularity_score = 95,                            -- New current value
    score_change_pct = ((95 - 85) / 85.0) * 100,     -- +11.76%
    updated_at = NOW()
WHERE skill_name = 'Python';
```

**Result: Same row, new columns**

| skill_name | popularity_score | previous_popularity_score | score_change_pct | previous_score_date |
|------------|------------------|---------------------------|------------------|---------------------|
| Python | 95 | 85 | +11.76 | 2024-09-01 |

---

### **Querying Type 3**
```sql
-- Skills with increasing popularity
SELECT 
    skill_name,
    popularity_score AS current_score,
    previous_popularity_score AS prev_score,
    score_change_pct,
    CASE 
        WHEN score_change_pct > 10 THEN 'Hot 🔥'
        WHEN score_change_pct > 0 THEN 'Rising 📈'
        WHEN score_change_pct < -10 THEN 'Declining 📉'
        ELSE 'Stable ➡️'
    END AS trend
FROM dim_skill
WHERE previous_popularity_score IS NOT NULL
ORDER BY score_change_pct DESC;
```

### **dbt Implementation**
```sql
-- models/gold/dim_skill.sql
{{
  config(
    materialized='table',
    unique_key='skill_name'
  )
}}

WITH current_scores AS (
    SELECT
        skill_name,
        COUNT(*) AS current_popularity_score
    FROM {{ ref('fct_job_skills') }} fs
    JOIN {{ ref('dim_date') }} d ON fs.scraped_date_sk = d.date_sk
    WHERE d.is_current_month = TRUE
    GROUP BY skill_name
),

previous_scores AS (
    SELECT
        skill_name,
        popularity_score AS previous_popularity_score,
        updated_at AS previous_score_date
    FROM {{ this }}  -- Self-reference to get last month's data
)

SELECT
    ROW_NUMBER() OVER (ORDER BY c.skill_name) AS skill_sk,
    c.skill_name,
    c.current_popularity_score AS popularity_score,
    p.previous_popularity_score,
    p.previous_score_date,
    CASE 
        WHEN p.previous_popularity_score IS NOT NULL THEN
            ROUND(((c.current_popularity_score - p.previous_popularity_score) / 
                   p.previous_popularity_score::DECIMAL) * 100, 2)
        ELSE NULL
    END AS score_change_pct,
    CURRENT_TIMESTAMP AS updated_at
FROM current_scores c
LEFT JOIN previous_scores p ON c.skill_name = p.skill_name
```

### **Pros & Cons**
✅ Simple queries (no date joins)  
✅ Less storage than Type 2  
✅ Easy to compare current vs previous  
✅ Good for trends  
❌ **Limited history** (only 1-2 versions)  
❌ Cannot do long-term historical analysis  
❌ Must decide which attributes to track  

### **CrawlJob Examples**
```sql
-- dim_skill (Current + Previous month popularity)
-- Enough for trend analysis without full history
```

---

## 🗂️ **SCD Type 4: Mini-Dimension**

### **Concept**
Tách **rapidly changing attributes** vào **separate table**.

### **When to Use**
- ✅ Some attributes change **VERY frequently** (daily/hourly)
- ✅ Majority of attributes change **slowly**
- ✅ Want to avoid bloating main dimension with too many Type 2 rows

### **Schema**
```sql
-- Main dimension (slow-changing - Type 2)
CREATE TABLE dim_company (
    company_sk          BIGINT PRIMARY KEY,
    company_name        VARCHAR NOT NULL,
    industry            VARCHAR,
    headquarters        VARCHAR,
    
    effective_date      DATE NOT NULL,
    expiration_date     DATE,
    is_current          BOOLEAN DEFAULT TRUE
);

-- Mini-dimension (fast-changing - separate table)
CREATE TABLE dim_company_metrics (
    metrics_sk              BIGINT PRIMARY KEY,
    company_sk              BIGINT NOT NULL,     -- FK to dim_company
    
    -- Rapidly changing metrics
    total_jobs_posted       INTEGER,             -- Changes daily
    avg_salary_offered      DECIMAL(12,2),       -- Changes weekly
    hiring_velocity         DECIMAL(5,2),        -- Jobs per week
    job_fill_rate           DECIMAL(3,2),        -- % of jobs filled
    
    -- Snapshot date
    snapshot_date           DATE NOT NULL,
    
    UNIQUE (company_sk, snapshot_date),
    FOREIGN KEY (company_sk) REFERENCES dim_company(company_sk)
);
```

### **Fact Table Links to BOTH**
```sql
CREATE TABLE fct_jobs (
    job_sk              BIGINT PRIMARY KEY,
    
    -- Link to main dimension
    company_sk          BIGINT NOT NULL,         -- → dim_company (slow-changing)
    
    -- Link to mini-dimension
    company_metrics_sk  BIGINT,                  -- → dim_company_metrics (snapshot)
    
    -- Other fields...
    scraped_date_sk     INTEGER NOT NULL,
    
    FOREIGN KEY (company_sk) REFERENCES dim_company(company_sk),
    FOREIGN KEY (company_metrics_sk) REFERENCES dim_company_metrics(metrics_sk)
);
```

### **Example**

**dim_company (Type 2 - changes rarely)**
| company_sk | company_name | industry | effective_date | is_current |
|------------|--------------|----------|----------------|------------|
| 1 | FPT Software | IT | 2024-01-01 | TRUE |

**dim_company_metrics (Type 4 - daily snapshots)**
| metrics_sk | company_sk | total_jobs_posted | avg_salary | snapshot_date |
|------------|------------|-------------------|------------|---------------|
| 101 | 1 | 45 | 25M | 2024-10-01 |
| 102 | 1 | 52 | 26M | 2024-10-02 |
| 103 | 1 | 48 | 25.5M | 2024-10-03 |

**fct_jobs**
| job_sk | company_sk | company_metrics_sk | scraped_date_sk |
|--------|------------|--------------------|-----------------|
| 1001 | 1 | 101 | 20241001 |
| 1002 | 1 | 102 | 20241002 |

---

### **Querying**
```sql
-- Jobs with company context + metrics snapshot
SELECT 
    f.job_title,
    c.company_name,
    c.industry,
    m.total_jobs_posted,
    m.avg_salary_offered,
    d.full_date
FROM fct_jobs f
JOIN dim_company c ON f.company_sk = c.company_sk
LEFT JOIN dim_company_metrics m ON f.company_metrics_sk = m.metrics_sk
JOIN dim_date d ON f.scraped_date_sk = d.date_sk
WHERE c.is_current = TRUE;
```

### **Pros & Cons**
✅ Separate slow vs fast-changing attributes  
✅ Reduces dimension bloat  
✅ Flexible snapshot strategy  
❌ Complex schema (2 tables instead of 1)  
❌ More complex queries (2 joins)  
❌ ETL complexity  

---

## 🎭 **SCD Type 6: Hybrid (1+2+3)**

### **Concept**
Kết hợp **Type 1 + Type 2 + Type 3** trong cùng một bảng.

### **Schema**
```sql
CREATE TABLE dim_company (
    company_sk              BIGINT PRIMARY KEY,
    company_name            VARCHAR NOT NULL,
    
    -- Type 1: Always current (overwrite)
    current_size            VARCHAR,             -- Latest size
    current_revenue         DECIMAL(15,2),       -- Latest revenue
    current_website         VARCHAR,             -- Latest URL
    
    -- Type 2: Historical (add rows)
    historical_size         VARCHAR,             -- Size at this version
    historical_headquarters VARCHAR,             -- HQ at this version
    effective_date          DATE NOT NULL,
    expiration_date         DATE,
    is_current              BOOLEAN DEFAULT TRUE,
    
    -- Type 3: Previous value (limited history)
    previous_size           VARCHAR,             -- Last known size
    previous_size_date      DATE,                -- When it changed
    
    updated_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Example**
| company_sk | company_name | current_size | historical_size | previous_size | effective_date | is_current |
|------------|--------------|--------------|-----------------|---------------|----------------|------------|
| 1 | FPT | 500+ | 201-500 | 51-200 | 2024-01-01 | FALSE |
| 2 | FPT | 500+ | 500+ | 201-500 | 2024-07-01 | TRUE |

- **current_size**: Always 500+ (Type 1 - overwritten)
- **historical_size**: Reflects size at that version (Type 2)
- **previous_size**: One step back (Type 3)

### **Pros & Cons**
✅ Maximum flexibility  
✅ Supports multiple query patterns  
❌ Very complex schema  
❌ High storage overhead  
❌ Difficult to maintain  
❌ Confusing for developers  

**Recommendation**: Only use if absolutely necessary. Usually Type 2 is sufficient.

---

## 🎯 **CrawlJob SCD Implementation Strategy**

### **Dimension → SCD Type Mapping**

| Dimension Table | SCD Type | Rationale |
|----------------|----------|-----------|
| `dim_date` | **Type 0** | Calendar is immutable |
| `dim_location` | **Type 0** | Cities/provinces rarely change |
| `dim_industry` | **Type 0** | Static taxonomy |
| `dim_job_category` | **Type 0** | Standard classification |
| `dim_source_site` | **Type 1** | URL/metrics don't need history |
| `dim_company` | **Type 2** | ✅ Track company evolution |
| `dim_skill` | **Type 3** | Current + previous month trend |

---

### **Why dim_company Uses Type 2?**

**Business Requirements**:
1. **Company Growth**: Track size changes (50 → 500 employees)
2. **Historical Salary Analysis**: "FPT's salary in 2023 vs 2024"
3. **Relocation Impact**: "Viettel moved HQ, how did it affect hiring?"
4. **Industry Pivot**: "Grab from Transportation → FinTech"

**Example Query**:
```sql
-- Jobs posted by FPT when they were mid-size (historical context)
SELECT 
    f.job_title,
    f.salary_max,
    c.company_size,
    c.effective_date,
    d.full_date AS job_posted_date
FROM fct_jobs f
JOIN dim_company c ON f.company_sk = c.company_sk
JOIN dim_date d ON f.scraped_date_sk = d.date_sk
WHERE c.company_name = 'FPT Software'
  AND c.company_size = '201-500'  -- Historical version
  AND d.full_date BETWEEN c.effective_date AND COALESCE(c.expiration_date, '9999-12-31');
```

---

### **Why dim_skill Uses Type 3?**

**Business Requirements**:
- Compare **current month** vs **previous month** popularity
- Don't need full history (too many changes)
- Simplified queries

**Example Query**:
```sql
-- Trending skills (up/down this month)
SELECT 
    skill_name,
    popularity_score AS current_score,
    previous_popularity_score AS prev_score,
    score_change_pct,
    CASE 
        WHEN score_change_pct > 20 THEN 'Hot 🔥'
        WHEN score_change_pct > 0 THEN 'Rising 📈'
        ELSE 'Declining 📉'
    END AS trend
FROM dim_skill
WHERE previous_popularity_score IS NOT NULL
ORDER BY score_change_pct DESC
LIMIT 10;
```

---

## 🔧 **dbt Best Practices for SCD**

### **1. Use Snapshots for Type 2** (Recommended)

dbt has built-in support for SCD Type 2 via **snapshots**.

```sql
-- snapshots/dim_company_snapshot.sql
{% snapshot dim_company_snapshot %}

{{
  config(
    target_schema='gold',
    unique_key='company_name',
    strategy='check',
    check_cols=['company_size', 'headquarters', 'industry']
  )
}}

SELECT
    company_name,
    company_size,
    company_type,
    industry,
    headquarters
FROM {{ ref('stg_companies') }}

{% endsnapshot %}
```

**Run**:
```bash
dbt snapshot --profiles-dir .
```

**Result**: Automatic SCD Type 2 tracking!
- `dbt_valid_from`: effective_date
- `dbt_valid_to`: expiration_date
- `dbt_updated_at`: updated_at

---

### **2. Manual Type 2 Implementation**

```sql
-- models/gold/dim_company.sql
{{
  config(
    materialized='incremental',
    unique_key='company_sk'
  )
}}

-- (See detailed implementation in Type 2 section above)
```

---

### **3. Type 3 with Self-Join**

```sql
-- models/gold/dim_skill.sql
WITH current_month AS (
    SELECT skill_name, COUNT(*) AS popularity
    FROM {{ ref('fct_job_skills') }}
    WHERE scraped_month = DATE_TRUNC('month', CURRENT_DATE)
    GROUP BY skill_name
),

previous_month AS (
    SELECT skill_name, popularity AS prev_popularity
    FROM {{ this }}  -- Self-reference
)

SELECT
    c.skill_name,
    c.popularity AS popularity_score,
    p.prev_popularity AS previous_popularity_score,
    ((c.popularity - p.prev_popularity) / p.prev_popularity::DECIMAL) * 100 AS score_change_pct
FROM current_month c
LEFT JOIN previous_month p USING (skill_name)
```

---

## 📚 **Summary: When to Use Each Type**

```
┌─────────────────────────────────────────────────────┐
│                 SCD Decision Tree                    │
└─────────────────────────────────────────────────────┘

Does the attribute EVER change?
│
├─ NO  → Type 0 (No tracking)
│         Examples: Country, Date of birth
│
└─ YES → Do you need historical tracking?
    │
    ├─ NO  → Type 1 (Overwrite)
    │         Examples: Typo fixes, latest metrics
    │
    └─ YES → How much history?
        │
        ├─ Full history  → Type 2 (Add row)
        │                   Examples: Company evolution, customer status
        │
        ├─ Limited (1-2 versions)  → Type 3 (Add column)
        │                             Examples: Previous month value
        │
        └─ Rapidly changing subset  → Type 4 (Mini-dimension)
                                       Examples: Daily metrics
```

---

## ✅ **Best Practices**

1. **Start Simple**: Most dimensions can use Type 0 or Type 1
2. **Type 2 When Needed**: Only if historical context truly matters
3. **Consider Storage**: Type 2 can explode row counts
4. **Index Properly**: `is_current`, `effective_date`, `business_key`
5. **Document Decisions**: Why each dimension uses specific SCD type
6. **Test Thoroughly**: Ensure SCD logic works correctly
7. **Monitor Performance**: Type 2 queries can be slow without proper indexes

---

## 🔍 **Testing SCD Implementation**

### **dbt Tests for Type 2**
```yaml
# models/gold/schema.yml
version: 2

models:
  - name: dim_company
    description: "Company dimension with SCD Type 2"
    
    tests:
      # Test 1: Only one current record per company
      - dbt_utils.unique_combination_of_columns:
          combination_of_columns:
            - company_name
            - is_current
          where: "is_current = TRUE"
      
      # Test 2: No gaps in effective/expiration dates
      - dbt_utils.expression_is_true:
          expression: "expiration_date IS NULL OR expiration_date >= effective_date"
      
      # Test 3: Current records have NULL expiration
      - dbt_utils.expression_is_true:
          expression: "is_current = FALSE OR expiration_date IS NULL"
          where: "is_current = TRUE"
    
    columns:
      - name: company_sk
        tests:
          - unique
          - not_null
      
      - name: company_name
        tests:
          - not_null
      
      - name: effective_date
        tests:
          - not_null
```

---

## 📖 **Further Reading**

- **Kimball Group**: "The Data Warehouse Toolkit" (Chapter on SCDs)
- **dbt Documentation**: [Snapshots](https://docs.getdbt.com/docs/build/snapshots)
- **CrawlJob Architecture**: `document/plan/DATA_WAREHOUSE_ARCHITECTURE.md`

---

**Last Updated**: October 5, 2025  
**Maintainer**: CrawlJob Team  
**Version**: 1.0
