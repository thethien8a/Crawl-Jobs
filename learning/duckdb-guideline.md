# DuckDB Complete Guideline - Hướng dẫn Toàn diện

## 📚 Mục lục
1. [Giới thiệu DuckDB](#1-giới-thiệu-duckdb)
2. [Installation & Setup](#2-installation--setup)
3. [Cơ bản với DuckDB CLI](#3-cơ-bản-với-duckdb-cli)
4. [Data Import/Export](#4-data-importexport)
5. [Querying Data](#5-querying-data)
6. [Aggregations & Window Functions](#6-aggregations--window-functions)
7. [Joins & Relationships](#7-joins--relationships)
8. [Advanced Features](#8-advanced-features)
9. [Python Integration](#9-python-integration)
10. [Best Practices](#10-best-practices)

---

## 1. Giới thiệu DuckDB

### 1.1. DuckDB là gì?

**DuckDB** là một **in-process SQL OLAP database** được thiết kế cho:
- ✅ **Analytics workloads** (phân tích dữ liệu)
- ✅ **Embedded database** (nhúng vào ứng dụng)
- ✅ **Fast queries** trên datasets lớn
- ✅ **Zero external dependencies**

### 1.2. Đặc điểm nổi bật

| Tính năng | Mô tả |
|-----------|-------|
| **Columnar Storage** | Lưu trữ theo cột → nhanh cho analytics |
| **In-Process** | Chạy trong process của app → không cần server |
| **Portable** | File `.duckdb` duy nhất, dễ backup/share |
| **SQL Standard** | PostgreSQL-compatible syntax |
| **Direct File Query** | Query CSV/Parquet/JSON trực tiếp |
| **Multi-threaded** | Tận dụng multi-core CPU |

### 1.3. So sánh với các DB khác

| Database | Type | Use Case |
|----------|------|----------|
| **DuckDB** | OLAP, Embedded | Analytics, data science, ETL |
| **PostgreSQL** | OLTP | Transactional apps, web apps |
| **SQLite** | OLTP, Embedded | Mobile apps, small datasets |
| **Snowflake** | OLAP, Cloud | Enterprise data warehouse |
| **Pandas** | DataFrame | Python data analysis (slower) |

---

## 2. Installation & Setup

### 2.1. Install DuckDB CLI

#### **Windows:**
```bash
# Download từ https://duckdb.org/docs/installation/
# Hoặc dùng Scoop
scoop install duckdb
```

#### **Linux/macOS:**
```bash
# Download binary
wget https://github.com/duckdb/duckdb/releases/download/v1.0.0/duckdb_cli-linux-amd64.zip
unzip duckdb_cli-linux-amd64.zip

# Hoặc dùng Homebrew (macOS)
brew install duckdb
```

### 2.2. Install Python Package

```bash
pip install duckdb
```

### 2.3. Verify Installation

```bash
# CLI version
duckdb --version

# Python version
python -c "import duckdb; print(duckdb.__version__)"
```

---

## 3. Cơ bản với DuckDB CLI

### 3.1. Khởi động DuckDB

#### **In-Memory Database (Temporary)**
```bash
duckdb
```
→ Data sẽ mất khi thoát

#### **Persistent Database (Lưu vào file)**
```bash
# Tạo hoặc mở file database
duckdb mydata.duckdb
```
→ Data được lưu vào `mydata.duckdb`

### 3.2. Basic Commands

#### **Help Commands**
```sql
.help                 -- Xem tất cả commands
.tables               -- List tất cả tables
.schema table_name    -- Xem schema của table
.databases            -- List databases
.quit hoặc Ctrl+D     -- Thoát
```

#### **Show Tables & Schemas**
```sql
-- List tất cả tables
SHOW TABLES;

-- List schemas
SHOW SCHEMAS;

-- List columns của table
DESCRIBE jobs;
PRAGMA table_info('jobs');

-- Xem CREATE statement
SELECT sql FROM sqlite_master WHERE name = 'jobs';
```

### 3.3. Tạo Tables

```sql
-- Tạo table đơn giản
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name VARCHAR,
    salary DOUBLE,
    department VARCHAR,
    hired_date DATE
);

-- Tạo table với constraints
CREATE TABLE jobs (
    job_url VARCHAR PRIMARY KEY,
    job_title VARCHAR NOT NULL,
    company_name VARCHAR NOT NULL,
    salary VARCHAR,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tạo table từ query
CREATE TABLE high_salary AS
SELECT * FROM employees WHERE salary > 50000;
```

### 3.4. Insert Data

```sql
-- Insert single row
INSERT INTO employees VALUES (1, 'Alice', 75000, 'IT', '2023-01-15');

-- Insert multiple rows
INSERT INTO employees VALUES
    (2, 'Bob', 65000, 'Sales', '2023-02-20'),
    (3, 'Carol', 80000, 'IT', '2023-03-10'),
    (4, 'Dave', 55000, 'HR', '2023-04-05');

-- Insert from SELECT
INSERT INTO high_salary
SELECT * FROM employees WHERE salary > 60000;
```

---

## 4. Data Import/Export

### 4.1. Direct File Querying (Killer Feature!)

#### **Query CSV Files**
```sql
-- Query CSV trực tiếp (auto-detect schema)
SELECT * FROM 'data.csv';

-- Với options
SELECT * FROM read_csv_auto('data.csv', header=true, delim=',');

-- Query CSV từ URL
SELECT * FROM 'https://example.com/data.csv';

-- Query gzipped CSV
SELECT * FROM read_csv_auto('data.csv.gz', compression='gzip');
```

#### **Query Parquet Files**
```sql
-- Query Parquet trực tiếp
SELECT * FROM 'data.parquet';

-- Multiple Parquet files (glob pattern)
SELECT * FROM 'data/*.parquet';
SELECT * FROM 'data/year=2023/month=*/day=*/data.parquet';
```

#### **Query JSON Files**
```sql
-- Query JSON file
SELECT * FROM read_json_auto('data.json');

-- Newline-delimited JSON
SELECT * FROM read_json_auto('data.ndjson', format='newline_delimited');
```

### 4.2. Import Data vào Tables

#### **Import CSV**
```sql
-- CREATE TABLE từ CSV
CREATE TABLE jobs AS
SELECT * FROM read_csv_auto('jobs.csv');

-- COPY INTO table (nhanh hơn INSERT)
COPY jobs FROM 'jobs.csv' (HEADER, DELIMITER ',');

-- Import với schema cụ thể
CREATE TABLE jobs (job_url VARCHAR, title VARCHAR, salary VARCHAR);
COPY jobs FROM 'jobs.csv' (HEADER);
```

#### **Import Parquet**
```sql
-- CREATE TABLE từ Parquet
CREATE TABLE jobs AS
SELECT * FROM 'jobs.parquet';

-- COPY từ multiple Parquet files
CREATE TABLE jobs AS
SELECT * FROM 'data/year=2023/**/*.parquet';
```

### 4.3. Export Data

#### **Export to CSV**
```sql
-- Export table to CSV
COPY jobs TO 'output.csv' (HEADER, DELIMITER ',');

-- Export query results
COPY (SELECT * FROM jobs WHERE salary IS NOT NULL)
TO 'high_salary_jobs.csv' (HEADER);
```

#### **Export to Parquet**
```sql
-- Export to Parquet (nén tốt, nhanh)
COPY jobs TO 'output.parquet' (FORMAT PARQUET);

-- With compression
COPY jobs TO 'output.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);
```

#### **Export to JSON**
```sql
-- Export to JSON
COPY jobs TO 'output.json';
```

---

## 5. Querying Data

### 5.1. SELECT Basics

```sql
-- Select all columns
SELECT * FROM jobs;

-- Select specific columns
SELECT job_title, company_name, salary FROM jobs;

-- With aliases
SELECT 
    job_title AS title,
    company_name AS company,
    salary AS pay
FROM jobs;

-- DISTINCT values
SELECT DISTINCT source_site FROM jobs;

-- LIMIT results
SELECT * FROM jobs LIMIT 10;
SELECT * FROM jobs LIMIT 10 OFFSET 20;  -- Pagination
```

### 5.2. WHERE Clause (Filtering)

```sql
-- Simple conditions
SELECT * FROM jobs WHERE salary > 50000;
SELECT * FROM jobs WHERE source_site = 'topcv';

-- Multiple conditions
SELECT * FROM jobs
WHERE salary > 30000
  AND source_site IN ('topcv', 'itviec')
  AND job_title LIKE '%Data%';

-- NULL handling
SELECT * FROM jobs WHERE salary IS NOT NULL;
SELECT * FROM jobs WHERE company_name IS NOT NULL;

-- Date filters
SELECT * FROM jobs
WHERE scraped_at >= '2025-01-01'
  AND scraped_at < '2025-02-01';

-- Pattern matching
SELECT * FROM jobs WHERE job_title LIKE '%Engineer%';
SELECT * FROM jobs WHERE job_title ILIKE '%engineer%';  -- Case-insensitive
SELECT * FROM jobs WHERE job_title ~ 'Data|Engineer';   -- Regex
```

### 5.3. ORDER BY

```sql
-- Ascending order (default)
SELECT * FROM jobs ORDER BY salary;

-- Descending order
SELECT * FROM jobs ORDER BY salary DESC;

-- Multiple columns
SELECT * FROM jobs
ORDER BY source_site ASC, salary DESC;

-- NULLS handling
SELECT * FROM jobs
ORDER BY salary DESC NULLS LAST;
```

### 5.4. GROUP BY & HAVING

```sql
-- Basic aggregation
SELECT 
    source_site,
    COUNT(*) AS total_jobs,
    AVG(CAST(salary AS DOUBLE)) AS avg_salary
FROM jobs
GROUP BY source_site;

-- With HAVING (filter aggregated results)
SELECT 
    company_name,
    COUNT(*) AS job_count
FROM jobs
GROUP BY company_name
HAVING COUNT(*) > 5
ORDER BY job_count DESC;

-- Multiple grouping columns
SELECT 
    source_site,
    DATE_TRUNC('month', scraped_at) AS month,
    COUNT(*) AS jobs_count
FROM jobs
GROUP BY source_site, month
ORDER BY month, source_site;
```

---

## 6. Aggregations & Window Functions

### 6.1. Aggregate Functions

```sql
-- Basic aggregates
SELECT 
    COUNT(*) AS total_jobs,
    COUNT(DISTINCT company_name) AS unique_companies,
    MIN(scraped_at) AS earliest_scrape,
    MAX(scraped_at) AS latest_scrape
FROM jobs;

-- Numeric aggregates
SELECT 
    AVG(salary) AS avg_salary,
    SUM(salary) AS total_salary,
    MIN(salary) AS min_salary,
    MAX(salary) AS max_salary,
    STDDEV(salary) AS salary_stddev
FROM jobs
WHERE salary IS NOT NULL;

-- String aggregation
SELECT 
    source_site,
    STRING_AGG(company_name, ', ' ORDER BY company_name) AS companies
FROM jobs
GROUP BY source_site;

-- LIST aggregation (DuckDB-specific)
SELECT 
    source_site,
    LIST(DISTINCT company_name) AS company_list
FROM jobs
GROUP BY source_site;
```

### 6.2. Window Functions

#### **ROW_NUMBER, RANK, DENSE_RANK**
```sql
-- Assign row numbers
SELECT 
    job_title,
    company_name,
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) AS row_num
FROM jobs;

-- Rank within groups
SELECT 
    source_site,
    company_name,
    COUNT(*) AS job_count,
    RANK() OVER (PARTITION BY source_site ORDER BY COUNT(*) DESC) AS rank
FROM jobs
GROUP BY source_site, company_name;
```

#### **LAG, LEAD**
```sql
-- Compare with previous/next row
SELECT 
    scraped_at,
    COUNT(*) AS daily_jobs,
    LAG(COUNT(*)) OVER (ORDER BY scraped_at) AS prev_day_jobs,
    LEAD(COUNT(*)) OVER (ORDER BY scraped_at) AS next_day_jobs
FROM jobs
GROUP BY scraped_at;
```

#### **FIRST_VALUE, LAST_VALUE**
```sql
-- Get first/last value in window
SELECT 
    job_title,
    salary,
    FIRST_VALUE(salary) OVER (ORDER BY salary) AS min_salary,
    LAST_VALUE(salary) OVER (ORDER BY salary) AS max_salary
FROM jobs;
```

#### **Running Totals**
```sql
-- Cumulative sum
SELECT 
    scraped_at,
    COUNT(*) AS daily_jobs,
    SUM(COUNT(*)) OVER (ORDER BY scraped_at) AS cumulative_jobs
FROM jobs
GROUP BY scraped_at;
```

---

## 7. Joins & Relationships

### 7.1. INNER JOIN

```sql
-- Join two tables
SELECT 
    j.job_title,
    j.salary,
    c.company_size,
    c.industry
FROM jobs j
INNER JOIN companies c ON j.company_name = c.company_name;
```

### 7.2. LEFT JOIN

```sql
-- Keep all jobs, even without company match
SELECT 
    j.job_title,
    j.company_name,
    c.company_size
FROM jobs j
LEFT JOIN companies c ON j.company_name = c.company_name;
```

### 7.3. RIGHT JOIN

```sql
-- Keep all companies, even without jobs
SELECT 
    c.company_name,
    c.industry,
    COUNT(j.job_url) AS job_count
FROM jobs j
RIGHT JOIN companies c ON j.company_name = c.company_name
GROUP BY c.company_name, c.industry;
```

### 7.4. FULL OUTER JOIN

```sql
-- Keep all records from both tables
SELECT 
    COALESCE(j.company_name, c.company_name) AS company,
    j.job_title,
    c.company_size
FROM jobs j
FULL OUTER JOIN companies c ON j.company_name = c.company_name;
```

### 7.5. CROSS JOIN

```sql
-- Cartesian product (mỗi row với mỗi row)
SELECT 
    s.site_name,
    d.date
FROM source_sites s
CROSS JOIN dates d;
```

---

## 8. Advanced Features

### 8.1. Common Table Expressions (CTEs)

```sql
-- Single CTE
WITH high_salary_jobs AS (
    SELECT * FROM jobs
    WHERE CAST(salary AS DOUBLE) > 50000
)
SELECT 
    source_site,
    COUNT(*) AS count
FROM high_salary_jobs
GROUP BY source_site;

-- Multiple CTEs
WITH 
    recent_jobs AS (
        SELECT * FROM jobs
        WHERE scraped_at >= CURRENT_DATE - INTERVAL '7' DAY
    ),
    company_stats AS (
        SELECT 
            company_name,
            COUNT(*) AS job_count,
            AVG(salary) AS avg_salary
        FROM recent_jobs
        GROUP BY company_name
    )
SELECT *
FROM company_stats
WHERE job_count > 5
ORDER BY avg_salary DESC;
```

### 8.2. UNION, INTERSECT, EXCEPT

```sql
-- UNION (combine results, remove duplicates)
SELECT job_title FROM jobs WHERE source_site = 'topcv'
UNION
SELECT job_title FROM jobs WHERE source_site = 'itviec';

-- UNION ALL (keep duplicates)
SELECT job_title FROM jobs WHERE source_site = 'topcv'
UNION ALL
SELECT job_title FROM jobs WHERE source_site = 'itviec';

-- INTERSECT (common rows)
SELECT job_title FROM jobs WHERE source_site = 'topcv'
INTERSECT
SELECT job_title FROM jobs WHERE source_site = 'itviec';

-- EXCEPT (rows in first but not in second)
SELECT job_title FROM jobs WHERE source_site = 'topcv'
EXCEPT
SELECT job_title FROM jobs WHERE source_site = 'itviec';
```

### 8.3. CASE Statements

```sql
-- Simple CASE
SELECT 
    job_title,
    salary,
    CASE 
        WHEN salary < 15000000 THEN 'Junior'
        WHEN salary BETWEEN 15000000 AND 30000000 THEN 'Mid'
        WHEN salary > 30000000 THEN 'Senior'
        ELSE 'Unknown'
    END AS level
FROM jobs;

-- Searched CASE
SELECT 
    source_site,
    COUNT(*) AS total,
    CASE 
        WHEN COUNT(*) > 1000 THEN 'High'
        WHEN COUNT(*) > 500 THEN 'Medium'
        ELSE 'Low'
    END AS volume
FROM jobs
GROUP BY source_site;
```

### 8.4. Subqueries

```sql
-- Scalar subquery
SELECT 
    job_title,
    salary,
    salary - (SELECT AVG(salary) FROM jobs) AS diff_from_avg
FROM jobs;

-- Correlated subquery
SELECT 
    j.job_title,
    j.company_name,
    j.salary
FROM jobs j
WHERE j.salary > (
    SELECT AVG(salary)
    FROM jobs j2
    WHERE j2.company_name = j.company_name
);

-- EXISTS
SELECT company_name
FROM companies c
WHERE EXISTS (
    SELECT 1 FROM jobs j
    WHERE j.company_name = c.company_name
);
```

### 8.5. Date/Time Functions

```sql
-- Current date/time
SELECT 
    CURRENT_DATE AS today,
    CURRENT_TIMESTAMP AS now,
    CURRENT_TIME AS time_now;

-- Date arithmetic
SELECT 
    CURRENT_DATE AS today,
    CURRENT_DATE - INTERVAL '7' DAY AS week_ago,
    CURRENT_DATE + INTERVAL '1' MONTH AS next_month;

-- Extract parts
SELECT 
    scraped_at,
    EXTRACT(YEAR FROM scraped_at) AS year,
    EXTRACT(MONTH FROM scraped_at) AS month,
    EXTRACT(DAY FROM scraped_at) AS day,
    EXTRACT(DOW FROM scraped_at) AS day_of_week;

-- Date truncation
SELECT 
    DATE_TRUNC('month', scraped_at) AS month,
    COUNT(*) AS jobs_count
FROM jobs
GROUP BY month;

-- Date formatting
SELECT 
    scraped_at,
    STRFTIME(scraped_at, '%Y-%m-%d') AS formatted_date,
    STRFTIME(scraped_at, '%Y-%m-%d %H:%M:%S') AS formatted_datetime
FROM jobs;
```

### 8.6. String Functions

```sql
-- String manipulation
SELECT 
    job_title,
    UPPER(job_title) AS uppercase,
    LOWER(job_title) AS lowercase,
    LENGTH(job_title) AS title_length,
    TRIM(job_title) AS trimmed,
    SUBSTRING(job_title, 1, 10) AS first_10_chars
FROM jobs;

-- Pattern matching & replacement
SELECT 
    job_title,
    REGEXP_REPLACE(job_title, '\\s+', ' ', 'g') AS normalized,
    REGEXP_MATCHES(job_title, 'Data|Engineer') AS is_tech_role
FROM jobs;

-- Concatenation
SELECT 
    company_name || ' - ' || job_title AS full_title,
    CONCAT(company_name, ' (', source_site, ')') AS company_with_source
FROM jobs;

-- Splitting strings
SELECT 
    job_title,
    STRING_SPLIT(job_title, ' ') AS words
FROM jobs;
```

### 8.7. Array/List Functions (DuckDB-specific)

```sql
-- Create arrays/lists
SELECT 
    [1, 2, 3, 4, 5] AS numbers,
    ['topcv', 'itviec', 'careerlink'] AS sites;

-- UNNEST (array to rows)
SELECT unnest([1, 2, 3, 4, 5]) AS num;

SELECT unnest(['topcv', 'itviec', 'careerlink']) AS site;

-- Array aggregation
SELECT 
    source_site,
    LIST(DISTINCT company_name) AS companies
FROM jobs
GROUP BY source_site;

-- Array operations
SELECT 
    [1, 2, 3] || [4, 5] AS concatenated,
    LIST_CONTAINS([1, 2, 3], 2) AS contains_two,
    LIST_HAS_ANY([1, 2, 3], [2, 4]) AS has_common,
    LEN([1, 2, 3, 4]) AS array_length;
```

### 8.8. JSON Functions

```sql
-- Parse JSON
SELECT 
    json_extract('{"name": "Alice", "age": 30}', '$.name') AS name,
    json_extract_string('{"name": "Alice"}', '$.name') AS name_str;

-- Create JSON
SELECT 
    TO_JSON(struct_pack(job_title := job_title, company := company_name)) AS job_json
FROM jobs;
```

---

## 9. Python Integration

### 9.1. Basic Python Usage

```python
import duckdb

# Connect to in-memory database
con = duckdb.connect(':memory:')

# Or connect to persistent file
con = duckdb.connect('mydata.duckdb')

# Execute query
result = con.execute("SELECT 42 AS answer").fetchall()
print(result)  # [(42,)]

# Fetch as DataFrame
import pandas as pd
df = con.execute("SELECT * FROM jobs").df()
```

### 9.2. Query Files Directly

```python
import duckdb

# Query CSV
result = duckdb.sql("SELECT * FROM 'data.csv'").df()

# Query Parquet
result = duckdb.sql("SELECT * FROM 'data.parquet'").df()

# Query multiple files
result = duckdb.sql("SELECT * FROM 'data/*.parquet'").df()
```

### 9.3. Query Pandas DataFrames

```python
import duckdb
import pandas as pd

# Create DataFrame
df = pd.DataFrame({
    'name': ['Alice', 'Bob', 'Carol'],
    'age': [25, 30, 35],
    'salary': [50000, 60000, 70000]
})

# Query DataFrame directly (no registration needed!)
result = duckdb.sql("SELECT * FROM df WHERE age > 25").df()
print(result)
```

### 9.4. Register DataFrames as Views

```python
import duckdb
import pandas as pd

con = duckdb.connect()

df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})

# Register as view
con.register('my_view', df)

# Query the view
result = con.execute("SELECT * FROM my_view").df()
```

### 9.5. Insert/Update from Python

```python
import duckdb

con = duckdb.connect('mydata.duckdb')

# Insert from Python list
data = [
    ('https://job1.com', 'Data Engineer', 'Company A'),
    ('https://job2.com', 'ML Engineer', 'Company B')
]

con.executemany(
    "INSERT INTO jobs (job_url, job_title, company_name) VALUES (?, ?, ?)",
    data
)

# Insert DataFrame
import pandas as pd
df = pd.DataFrame({
    'job_url': ['https://job3.com'],
    'job_title': ['DevOps Engineer'],
    'company_name': ['Company C']
})

con.execute("INSERT INTO jobs SELECT * FROM df")
```

### 9.6. Load/Save DuckDB with Pandas

```python
import duckdb
import pandas as pd

# Load DuckDB table to Pandas
con = duckdb.connect('mydata.duckdb')
df = con.execute("SELECT * FROM jobs").df()

# Save Pandas to DuckDB
df.to_sql('jobs', con, if_exists='replace')

# Or use DuckDB COPY (faster)
con.execute("CREATE TABLE jobs AS SELECT * FROM df")
```

---

## 10. Best Practices

### 10.1. Performance Optimization

#### **Use Parquet instead of CSV**
```sql
-- ❌ Slow (CSV parsing)
SELECT * FROM 'large_data.csv';

-- ✅ Fast (columnar format)
SELECT * FROM 'large_data.parquet';
```

#### **Filter early, aggregate late**
```sql
-- ❌ Inefficient
SELECT company_name, COUNT(*)
FROM (SELECT * FROM jobs)
WHERE source_site = 'topcv'
GROUP BY company_name;

-- ✅ Efficient
SELECT company_name, COUNT(*)
FROM jobs
WHERE source_site = 'topcv'
GROUP BY company_name;
```

#### **Use LIMIT for exploratory queries**
```sql
-- ❌ Process all 1M rows
SELECT * FROM huge_table;

-- ✅ Process only 100 rows
SELECT * FROM huge_table LIMIT 100;
```

#### **Analyze query plans**
```sql
-- Xem execution plan
EXPLAIN SELECT * FROM jobs WHERE salary > 50000;

-- Xem plan với execution time
EXPLAIN ANALYZE SELECT * FROM jobs WHERE salary > 50000;
```

### 10.2. Data Type Best Practices

```sql
-- ✅ Use appropriate types
CREATE TABLE jobs (
    id INTEGER,
    salary DOUBLE,       -- Not VARCHAR
    scraped_at TIMESTAMP, -- Not VARCHAR
    is_remote BOOLEAN    -- Not VARCHAR
);

-- ❌ Avoid storing everything as VARCHAR
CREATE TABLE jobs (
    id VARCHAR,
    salary VARCHAR,
    scraped_at VARCHAR
);
```

### 10.3. Schema Organization

```sql
-- Create schemas for organization
CREATE SCHEMA bronze;
CREATE SCHEMA silver;
CREATE SCHEMA gold;

-- Create tables in schemas
CREATE TABLE bronze.raw_jobs AS SELECT * FROM 'raw.parquet';
CREATE TABLE silver.cleaned_jobs AS SELECT * FROM bronze.raw_jobs WHERE ...;
CREATE TABLE gold.aggregated_jobs AS SELECT ... FROM silver.cleaned_jobs;
```

### 10.4. Backup & Restore

```bash
# Backup (copy .duckdb file)
cp mydata.duckdb mydata_backup_$(date +%Y%m%d).duckdb

# Export to Parquet (portable)
duckdb mydata.duckdb "COPY jobs TO 'jobs_backup.parquet' (FORMAT PARQUET)"
```

### 10.5. Security

```python
# ✅ Use parameterized queries (avoid SQL injection)
con.execute("SELECT * FROM jobs WHERE source_site = ?", ['topcv'])

# ❌ Never concatenate user input
user_input = "topcv'; DROP TABLE jobs; --"
con.execute(f"SELECT * FROM jobs WHERE source_site = '{user_input}'")  # DANGEROUS!
```

---

## 11. Common Use Cases

### 11.1. ETL Pipeline

```python
import duckdb

con = duckdb.connect('warehouse.duckdb')

# Extract (from CSV)
con.execute("""
    CREATE TABLE bronze.raw_jobs AS
    SELECT * FROM 'data/*.csv'
""")

# Transform (clean & normalize)
con.execute("""
    CREATE TABLE silver.cleaned_jobs AS
    SELECT 
        job_url,
        TRIM(LOWER(company_name)) AS company_name,
        REGEXP_REPLACE(salary, '\\s+', ' ', 'g') AS salary,
        DATE(scraped_at) AS scraped_date
    FROM bronze.raw_jobs
    WHERE job_url IS NOT NULL
""")

# Load (aggregates)
con.execute("""
    CREATE TABLE gold.company_stats AS
    SELECT 
        company_name,
        COUNT(*) AS total_jobs,
        AVG(CAST(salary AS DOUBLE)) AS avg_salary
    FROM silver.cleaned_jobs
    GROUP BY company_name
""")
```

### 11.2. Data Analysis

```python
import duckdb
import matplotlib.pyplot as plt

con = duckdb.connect('warehouse.duckdb')

# Analyze job trends
df = con.execute("""
    SELECT 
        DATE_TRUNC('month', scraped_at) AS month,
        source_site,
        COUNT(*) AS job_count
    FROM jobs
    GROUP BY month, source_site
    ORDER BY month
""").df()

# Plot
df.pivot(index='month', columns='source_site', values='job_count').plot(kind='line')
plt.show()
```

### 11.3. Data Deduplication

```sql
-- Find duplicates
SELECT 
    job_url,
    COUNT(*) AS dup_count
FROM jobs
GROUP BY job_url
HAVING COUNT(*) > 1;

-- Remove duplicates (keep first)
CREATE TABLE jobs_dedup AS
SELECT * FROM (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY job_url ORDER BY scraped_at DESC) AS rn
    FROM jobs
)
WHERE rn = 1;
```

---

## 12. Tổng kết

### ✅ Key Takeaways

1. **DuckDB = OLAP + Embedded + Fast**: Tối ưu cho analytics, không cần server
2. **Direct File Query**: Query CSV/Parquet trực tiếp, không cần import
3. **PostgreSQL-compatible SQL**: Syntax gần giống PostgreSQL
4. **Python Integration**: Tích hợp tốt với Pandas, NumPy
5. **Columnar Storage**: Nhanh cho aggregate queries
6. **Single-file Database**: Dễ backup, share, portable

### 📚 Resources

- [Official Documentation](https://duckdb.org/docs/)
- [SQL Introduction](https://duckdb.org/docs/sql/introduction)
- [Python API](https://duckdb.org/docs/api/python/overview)
- [Performance Guide](https://duckdb.org/docs/guides/performance/overview)
- [dbt-duckdb Adapter](https://github.com/duckdb/dbt-duckdb)

### 🎯 Next Steps

1. **Practice với real datasets**: Download Kaggle datasets, query với DuckDB
2. **Build ETL pipelines**: Dùng DuckDB cho Bronze-Silver-Gold architecture
3. **Integrate với dbt**: Sử dụng dbt-duckdb cho data transformations
4. **Explore extensions**: Install extensions như `spatial`, `httpfs`, `json`

```sql
-- Install extensions
INSTALL spatial;
LOAD spatial;

-- Query remote files
INSTALL httpfs;
LOAD httpfs;
SELECT * FROM 'https://example.com/data.parquet';
```

---

**Happy Querying with DuckDB! 🦆**
