# SQL Dialect trong dbt Tests - DuckDB vs PostgreSQL

## 🎯 **Câu trả lời ngắn gọn:**

**SQL trong dbt tests phụ thuộc vào DATABASE ADAPTER bạn đang dùng**, KHÔNG phải một SQL dialect cố định.

Trong project CrawlJob của bạn:
- **Adapter**: `duckdb` (định nghĩa trong `profiles.yml`)
- **SQL Dialect**: **DuckDB SQL** (rất gần với PostgreSQL nhưng có khác biệt)

---

## 📊 **Database Adapter quyết định SQL Dialect**

### Cách dbt xác định SQL Dialect

```yaml
# dbt_crawjob/profiles.yml
crawljob:
  target: dev
  outputs:
    dev:
      type: duckdb          # ← Adapter type quyết định SQL dialect
      path: "D:\\...\\warehouse.duckdb"
```

| Adapter | SQL Dialect | Use Case |
|---------|-------------|----------|
| `duckdb` | **DuckDB SQL** | OLAP, analytics, embedded database |
| `postgres` | **PostgreSQL** | OLTP, general purpose |
| `snowflake` | **Snowflake SQL** | Cloud data warehouse |
| `bigquery` | **BigQuery Standard SQL** | Google Cloud |
| `redshift` | **Amazon Redshift SQL** (PostgreSQL-like) | AWS data warehouse |
| `databricks` | **Spark SQL** | Lakehouse platform |

---

## 🦆 **DuckDB SQL - Những điểm khác biệt với PostgreSQL**

### 1. **Similarities (Giống PostgreSQL)**

DuckDB được **thiết kế gần giống PostgreSQL** về syntax:

#### ✅ **Cú pháp cơ bản giống nhau:**
```sql
-- Standard SQL syntax
SELECT column1, column2
FROM table_name
WHERE condition
GROUP BY column1
HAVING COUNT(*) > 1
ORDER BY column1;

-- INTERVAL syntax (giống PostgreSQL)
CURRENT_DATE - INTERVAL '7' DAYS

-- String functions
TRIM(column_name)
LOWER(column_name)
REGEXP_REPLACE(column, '\\s+', ' ', 'g')

-- CTEs (Common Table Expressions)
WITH cte AS (
  SELECT * FROM table
)
SELECT * FROM cte;
```

#### ✅ **Data types tương tự:**
```sql
-- Numeric types
INTEGER, BIGINT, DOUBLE, DECIMAL(10,2)

-- String types
VARCHAR, TEXT

-- Date/Time types
DATE, TIMESTAMP, TIMESTAMPTZ

-- Boolean
BOOLEAN

-- Arrays & Structs
INTEGER[], STRUCT(field1 VARCHAR, field2 INTEGER)
```

---

### 2. **Differences (Khác với PostgreSQL)**

#### ❌ **DuckDB KHÔNG hỗ trợ:**

##### **a. ENUM types**
```sql
-- PostgreSQL (CÓ)
CREATE TYPE source_site_enum AS ENUM ('topcv', 'itviec', 'careerlink');

-- DuckDB (KHÔNG CÓ)
-- Phải dùng CHECK constraint hoặc validate trong test
```

##### **b. Procedural SQL (PL/pgSQL)**
```sql
-- PostgreSQL (CÓ)
CREATE FUNCTION my_function() RETURNS INTEGER AS $$
BEGIN
  RETURN 42;
END;
$$ LANGUAGE plpgsql;

-- DuckDB (KHÔNG CÓ)
-- Chỉ có scalar functions, không có stored procedures
```

##### **c. Indexes & Constraints như PostgreSQL**
```sql
-- PostgreSQL (CÓ)
CREATE UNIQUE INDEX idx_url ON jobs(job_url);
ALTER TABLE jobs ADD CONSTRAINT fk_company FOREIGN KEY ...;

-- DuckDB (CÓ GI...
-- Constraints hoạt động khác, ít tính năng hơn
```

#### ✅ **DuckDB CÓ THÊM:**

##### **a. Direct File Querying**
```sql
-- DuckDB (ĐẶC BIỆT)
SELECT * FROM 'data.csv';
SELECT * FROM 'data.parquet';
SELECT * FROM read_parquet('s3://bucket/file.parquet');

-- PostgreSQL không có tính năng này
```

##### **b. UNNEST function (như PostgreSQL array_to_rows)**
```sql
-- DuckDB
SELECT unnest(['topcv', 'itviec', 'careerlink']) AS site;

-- PostgreSQL (tương đương)
SELECT unnest(ARRAY['topcv', 'itviec', 'careerlink']) AS site;
```

##### **c. LIST type (array động)**
```sql
-- DuckDB
SELECT [1, 2, 3] AS my_list;
SELECT list_value(1, 2, 3) AS my_list;

-- PostgreSQL dùng ARRAY
SELECT ARRAY[1, 2, 3] AS my_array;
```

---

## 🔧 **Ví dụ: Custom Tests với DuckDB SQL**

### **Test 1: Valid Source Site (DuckDB-specific)**

```sql
-- dbt_crawjob/macros/test_valid_source_site.sql
{% test valid_source_site(model, column_name) %}

-- ✅ DuckDB: Dùng UNNEST để tạo inline list
WITH valid_sites AS (
  SELECT unnest([
    'topcv', 'itviec', 'careerlink', 'careerviet',
    'job123', 'joboko', 'jobsgo', 'jobstreet',
    'linkedin', 'vietnamworks'
  ]) AS site
)
SELECT *
FROM {{ model }}
WHERE {{ column_name }} NOT IN (SELECT site FROM valid_sites)
   OR {{ column_name }} IS NULL

{% endtest %}
```

**Nếu dùng PostgreSQL adapter, cần viết:**
```sql
-- PostgreSQL version
WITH valid_sites AS (
  SELECT unnest(ARRAY[  -- ← ARRAY thay vì []
    'topcv', 'itviec', 'careerlink', 'careerviet',
    'job123', 'joboko', 'jobsgo', 'jobstreet',
    'linkedin', 'vietnamworks'
  ]) AS site
)
SELECT *
FROM {{ model }}
WHERE {{ column_name }} NOT IN (SELECT site FROM valid_sites)
   OR {{ column_name }} IS NULL
```

### **Test 2: Date Interval (Giống nhau)**

```sql
-- macros/test_is_recent.sql
{% test is_recent(model, column_name, days_ago=7) %}

-- ✅ Cú pháp này GIỐNG NHAU cho cả DuckDB và PostgreSQL
SELECT *
FROM {{ model }}
WHERE {{ column_name }} < CURRENT_DATE - INTERVAL '{{ days_ago }}' DAYS
   OR {{ column_name }} IS NULL

{% endtest %}
```

### **Test 3: Regex Replace (DuckDB có thể khác)**

```sql
-- DuckDB
SELECT regexp_replace(text, '\\s+', ' ', 'g')

-- PostgreSQL
SELECT regexp_replace(text, '\\s+', ' ', 'g')  -- Giống nhau!
```

---

## 🎓 **Best Practices: Viết SQL Cross-Database Compatible**

### **1. Dùng cú pháp Standard SQL khi có thể**

```sql
-- ✅ GOOD: Standard SQL (works everywhere)
SELECT 
  COUNT(*) AS total,
  AVG(salary) AS avg_salary
FROM jobs
WHERE created_at >= CURRENT_DATE - INTERVAL '7' DAY
GROUP BY company_name;

-- ❌ BAD: DuckDB-specific
SELECT * FROM read_csv_auto('file.csv');
```

### **2. Tránh database-specific features trong generic tests**

```sql
-- ✅ GOOD: Generic, works on all databases
{% test not_null(model, column_name) %}
SELECT *
FROM {{ model }}
WHERE {{ column_name }} IS NULL
{% endtest %}

-- ❌ BAD: DuckDB-specific (dùng LIST syntax)
WITH valid_values AS (
  SELECT unnest([1, 2, 3]) AS val  -- ← Chỉ work với DuckDB
)
...
```

### **3. Dùng Jinja để handle differences**

```sql
{% test valid_values(model, column_name, valid_list) %}

WITH valid_values AS (
  {% if target.type == 'duckdb' %}
    -- DuckDB syntax
    SELECT unnest({{ valid_list }}) AS val
  {% elif target.type == 'postgres' %}
    -- PostgreSQL syntax
    SELECT unnest(ARRAY{{ valid_list }}) AS val
  {% elif target.type == 'snowflake' %}
    -- Snowflake syntax
    SELECT value AS val FROM TABLE(FLATTEN(ARRAY_CONSTRUCT{{ valid_list }}))
  {% endif %}
)
SELECT *
FROM {{ model }}
WHERE {{ column_name }} NOT IN (SELECT val FROM valid_values)

{% endtest %}
```

### **4. Test với target database trước khi deploy**

```bash
# Debug compiled SQL
dbt compile --profiles-dir .

# Xem compiled SQL trong target/compiled/
cat target/compiled/crawljob/models/silver/stg_jobs.sql
```

---

## 🔍 **Kiểm tra SQL Dialect của bạn**

### **Cách 1: Xem adapter type**

```bash
dbt debug --profiles-dir .
```

Output:
```
Connection test: [OK connection ok]

Configuration:
  profiles.yml file [OK found and valid]
  dbt_project.yml file [OK found and valid]

Required dependencies:
 - git [OK found]

Connection:
  database: duckdb
  schema: main
  path: D:\Practice\Scrapy\CrawlJob\DuckDB\warehouse.duckdb
  Connection test: [OK connection ok]
```

### **Cách 2: Query trong DuckDB CLI**

```bash
# Mở DuckDB CLI
duckdb D:\Practice\Scrapy\CrawlJob\DuckDB\warehouse.duckdb

# Test DuckDB-specific features
SELECT unnest([1, 2, 3]) AS num;
SELECT * FROM 'file.csv';  -- Direct file query
```

### **Cách 3: Compile và xem SQL**

```bash
cd dbt_crawjob
dbt compile --profiles-dir . -s stg_jobs

# Xem compiled SQL
cat target/compiled/crawljob/models/silver/stg_jobs.sql
```

---

## 📚 **DuckDB SQL Features Used trong Tests**

### **1. INTERVAL (Standard SQL)**
```sql
-- ✅ Works in DuckDB, PostgreSQL, most databases
CURRENT_DATE - INTERVAL '7' DAYS
CURRENT_TIMESTAMP - INTERVAL '1' HOUR
```

### **2. REGEXP Functions**
```sql
-- ✅ DuckDB supports PostgreSQL-style regex
regexp_replace(text, 'pattern', 'replacement', 'flags')
regexp_matches(text, 'pattern')
```

### **3. String Functions**
```sql
-- ✅ Standard functions
TRIM(text)
LOWER(text)
UPPER(text)
CONCAT(str1, str2)
LENGTH(text)

-- ✅ DuckDB-specific (cũng có trong PostgreSQL)
LIKE 'pattern'
ILIKE 'pattern'  -- Case-insensitive LIKE
```

### **4. Aggregate Functions**
```sql
-- ✅ Standard aggregates
COUNT(*), COUNT(DISTINCT col)
SUM(col), AVG(col)
MIN(col), MAX(col)
```

### **5. Window Functions**
```sql
-- ✅ Works in DuckDB
ROW_NUMBER() OVER (PARTITION BY col ORDER BY col2)
RANK() OVER (...)
LAG(col) OVER (...)
```

---

## ⚠️ **Common Pitfalls khi viết Tests**

### **Pitfall 1: Hardcode table/schema names**

```sql
-- ❌ BAD: Hard-coded
SELECT * FROM bronze.jobs WHERE ...

-- ✅ GOOD: Use Jinja
SELECT * FROM {{ source('bronze', 'jobs') }} WHERE ...
```

### **Pitfall 2: Dùng database-specific syntax**

```sql
-- ❌ BAD: PostgreSQL-specific
SELECT col::INTEGER FROM table;

-- ✅ GOOD: Standard CAST
SELECT CAST(col AS INTEGER) FROM table;
```

### **Pitfall 3: Thiếu NULL handling**

```sql
-- ❌ BAD: NULL không được handle
WHERE {{ column_name }} < CURRENT_DATE

-- ✅ GOOD: Handle NULL
WHERE {{ column_name }} < CURRENT_DATE
   OR {{ column_name }} IS NULL
```

---

## 🎯 **Tóm tắt**

### ✅ **Key Takeaways**

1. **SQL dialect = Database adapter** (DuckDB, PostgreSQL, Snowflake, etc.)
2. **Project của bạn dùng DuckDB SQL** (định nghĩa trong `profiles.yml`)
3. **DuckDB SQL ≈ 95% giống PostgreSQL**, nhưng có khác biệt:
   - DuckDB: `unnest([...])`, direct file query
   - PostgreSQL: `unnest(ARRAY[...])`, no file query
4. **Dùng Standard SQL** khi có thể để tests tái sử dụng
5. **Dùng Jinja `{% if target.type %}` để handle differences**

### 📖 **Resources**

- [DuckDB SQL Introduction](https://duckdb.org/docs/sql/introduction)
- [DuckDB vs PostgreSQL](https://duckdb.org/docs/guides/database_integration/postgres)
- [dbt Adapters](https://docs.getdbt.com/docs/supported-data-platforms)
- [dbt Jinja Context](https://docs.getdbt.com/reference/dbt-jinja-functions/target)

---

## 💡 **Recommendation cho Project CrawlJob**

Vì bạn đang dùng **DuckDB adapter**, các tests hiện tại:

✅ **Đã đúng với DuckDB:**
- `test_valid_url.sql` - ✅ Standard SQL
- `test_is_recent.sql` - ✅ INTERVAL syntax works
- `test_valid_source_site.sql` - ✅ `unnest([...])` là DuckDB syntax

⚠️ **Nếu muốn switch sang PostgreSQL sau này:**
Cần sửa `unnest([...])` → `unnest(ARRAY[...])`

💡 **Recommendation:**
Giữ nguyên DuckDB syntax vì:
1. Project hiện tại dùng DuckDB (OLAP, analytics)
2. DuckDB nhanh hơn cho analytics workload
3. Không cần switch sang PostgreSQL trong tương lai gần

Nếu cần portable, dùng Jinja `{% if target.type == 'duckdb' %}` để handle!
