# dbt Testing - Hướng dẫn Toàn diện

## 📚 Mục lục
1. [Tổng quan về dbt Tests](#1-tổng-quan-về-dbt-tests)
2. [Singular Tests](#2-singular-tests)
3. [Generic Tests](#3-generic-tests)
4. [Custom Generic Tests](#4-custom-generic-tests)
5. [Best Practices](#5-best-practices)
6. [Ví dụ Thực tế cho Project CrawlJob](#6-ví-dụ-thực-tế-cho-project-crawljob)

---

## 1. Tổng quan về dbt Tests

### 1.1. Hai loại Tests trong dbt

| Loại | Vị trí | Tái sử dụng | Use Case |
|------|--------|-------------|----------|
| **Singular Tests** | `tests/*.sql` | ❌ Không | Tests đặc thù cho 1 model/case cụ thể |
| **Generic Tests** | `macros/tests/*.sql` + YAML | ✅ Có | Tests tái sử dụng cho nhiều models/columns |

### 1.2. Built-in Generic Tests

dbt cung cấp sẵn 4 generic tests:

| Test | Kiểm tra | Ví dụ |
|------|----------|-------|
| `unique` | Column không có giá trị trùng lặp | `job_url` phải unique |
| `not_null` | Column không có giá trị NULL | `job_title` không được NULL |
| `accepted_values` | Column chỉ chứa giá trị trong list cho phép | `source_site` chỉ có [topcv, itviec, ...] |
| `relationships` | Foreign key tồn tại trong bảng khác | `company_id` phải tồn tại trong `dim_company` |

---

## 2. Singular Tests

### 2.1. Định nghĩa

**Singular Tests** là SQL queries trong thư mục `tests/`, mỗi file là 1 test riêng biệt.

**Quy tắc:**
- Test **PASS** nếu query trả về **0 rows**
- Test **FAIL** nếu query trả về **>0 rows** (mỗi row là 1 lỗi)

### 2.2. Cấu trúc thư mục

```
dbt_crawjob/
├── tests/
│   ├── .gitkeep
│   ├── exist_today.sql          ← Singular test
│   ├── no_duplicate_urls.sql    ← Singular test
│   └── schema.yml               ← Metadata (optional)
```

### 2.3. Ví dụ: Singular Test có sẵn

**File: `tests/exist_today.sql`**
```sql
-- This test PASSES if data exists for CURRENT_DATE, and FAILS if no data exists.
SELECT
    'No data scraped for today' AS error_message
FROM (
    SELECT COUNT(*) as total
    FROM {{ source('bronze', 'jobs') }}
    WHERE scraped_date = CURRENT_DATE
)
WHERE total = 0
```

**Giải thích:**
- Nếu có data hôm nay → `total > 0` → WHERE false → 0 rows → **PASS**
- Nếu không có data → `total = 0` → WHERE true → 1 row → **FAIL**

### 2.4. Thêm Singular Tests

**File: `tests/no_future_deadlines.sql`**
```sql
-- Test FAILS if there are jobs with deadlines in the past
SELECT
    job_url,
    job_deadline,
    'Job deadline is in the past' AS error_message
FROM {{ ref('stg_jobs') }}
WHERE job_deadline < CURRENT_DATE
  AND job_deadline IS NOT NULL
```

**File: `tests/valid_salary_format.sql`**
```sql
-- Test FAILS if salary doesn't match expected patterns
SELECT
    job_url,
    salary,
    'Invalid salary format' AS error_message
FROM {{ ref('stg_jobs') }}
WHERE salary IS NOT NULL
  AND salary NOT LIKE '%VND%'
  AND salary NOT LIKE '%USD%'
  AND salary NOT LIKE 'Negotiate%'
```

### 2.5. Chạy Singular Tests

```bash
# Chạy tất cả tests
dbt test --profiles-dir .

# Chạy chỉ singular tests
dbt test --profiles-dir . --select test_type:singular

# Chạy 1 test cụ thể
dbt test --profiles-dir . --select exist_today
```

---

## 3. Generic Tests

### 3.1. Định nghĩa

**Generic Tests** là tests được **định nghĩa trong YAML** (`schema.yml`) và **áp dụng cho columns/models**.

### 3.2. Sử dụng Built-in Generic Tests

**File: `models/bronze/schema.yml`**
```yaml
version: 2

models:
  - name: jobs
    description: "Raw job data synced from PostgreSQL"
    columns:
      - name: job_url
        description: "Unique URL of the job posting"
        data_tests:
          - unique                # ← Generic test: job_url phải unique
          - not_null              # ← Generic test: job_url không NULL
      
      - name: source_site
        description: "Source website name"
        data_tests:
          - not_null
          - accepted_values:      # ← Generic test với parameters
              values: ['topcv', 'itviec', 'careerlink', 'careerviet', 
                       'job123', 'joboko', 'jobsgo', 'jobstreet', 
                       'linkedin', 'vietnamworks']
      
      - name: scraped_at
        description: "Timestamp when data was scraped"
        data_tests:
          - not_null
```

**File: `models/silver/schema.yml`**
```yaml
version: 2

models:
  - name: stg_jobs
    description: "Staging layer for jobs with normalized data"
    columns:
      - name: job_url
        data_tests:
          - unique
          - not_null
      
      - name: company_name
        data_tests:
          - not_null
      
      - name: scraped_date
        data_tests:
          - not_null
```

### 3.3. Relationships Test (Foreign Key)

**File: `models/gold/schema.yml`**
```yaml
version: 2

models:
  - name: fct_jobs
    description: "Job facts table"
    columns:
      - name: company_name
        description: "Foreign key to dim_company"
        data_tests:
          - relationships:        # ← Test foreign key
              to: ref('dim_company')
              field: company_name
```

**Ý nghĩa:** Mọi `company_name` trong `fct_jobs` phải tồn tại trong `dim_company.company_name`.

### 3.4. Test với Severity (Warn vs Error)

```yaml
models:
  - name: stg_jobs
    columns:
      - name: salary
        data_tests:
          - not_null:
              severity: warn      # ← WARN (không fail build)
      
      - name: job_url
        data_tests:
          - unique:
              severity: error     # ← ERROR (fail build) - mặc định
```

**Severity levels:**
- **`error`** (mặc định): Test fail → `dbt test` returns exit code 1
- **`warn`**: Test fail → chỉ warning, không fail build

---

## 4. Custom Generic Tests

### 4.1. Tại sao cần Custom Generic Tests?

Built-in tests (unique, not_null, etc.) chỉ cover các cases đơn giản. Bạn cần **custom tests** cho:
- Business logic phức tạp
- Tests tái sử dụng nhiều lần
- Tests với parameters linh hoạt

### 4.2. Vị trí định nghĩa

**Custom Generic Tests** được định nghĩa trong thư mục `macros/`:

```
dbt_crawjob/
├── macros/
│   ├── .gitkeep
│   ├── test_is_positive.sql           ← Custom test
│   ├── test_is_recent.sql             ← Custom test
│   ├── test_valid_url.sql             ← Custom test
│   └── test_has_data_for_date.sql     ← Custom test
```

### 4.3. Cú pháp Custom Generic Test

**Template:**
```sql
{% test test_name(model, column_name, param1, param2) %}

SELECT *
FROM {{ model }}
WHERE {{ column_name }} ... -- logic kiểm tra
  -- Test FAILS if query returns rows

{% endtest %}
```

**Quy tắc:**
- Macro name phải bắt đầu bằng `test_`
- Nhận `model` và `column_name` (hoặc chỉ `model` cho model-level test)
- Return rows → FAIL, 0 rows → PASS

### 4.4. Ví dụ 1: Test Column là Positive Number

**File: `macros/test_is_positive.sql`**
```sql
{% test is_positive(model, column_name) %}

SELECT *
FROM {{ model }}
WHERE {{ column_name }} <= 0
   OR {{ column_name }} IS NULL

{% endtest %}
```

**Sử dụng:**
```yaml
# models/gold/schema.yml
models:
  - name: dim_company
    columns:
      - name: total_jobs
        data_tests:
          - is_positive    # ← Sử dụng custom test
```

**Giải thích:**
- Test kiểm tra `total_jobs > 0`
- Nếu có row nào `<= 0` hoặc NULL → Test FAIL

### 4.5. Ví dụ 2: Test URL hợp lệ

**File: `macros/test_valid_url.sql`**
```sql
{% test valid_url(model, column_name) %}

SELECT *
FROM {{ model }}
WHERE {{ column_name }} IS NOT NULL
  AND NOT (
    {{ column_name }} LIKE 'http://%'
    OR {{ column_name }} LIKE 'https://%'
  )

{% endtest %}
```

**Sử dụng:**
```yaml
# models/bronze/schema.yml
models:
  - name: jobs
    columns:
      - name: job_url
        data_tests:
          - valid_url
```

### 4.6. Ví dụ 3: Test Data Freshness (có data trong N ngày)

**File: `macros/test_is_recent.sql`**
```sql
{% test is_recent(model, column_name, days_ago=7) %}

SELECT *
FROM {{ model }}
WHERE {{ column_name }} < CURRENT_DATE - INTERVAL '{{ days_ago }}' DAYS
   OR {{ column_name }} IS NULL

{% endtest %}
```

**Sử dụng:**
```yaml
models:
  - name: jobs
    columns:
      - name: scraped_at
        data_tests:
          - is_recent:
              days_ago: 3    # ← Parameter: data phải mới trong 3 ngày
```

**Giải thích:**
- Test kiểm tra `scraped_at` không cũ hơn 3 ngày
- Nếu có row nào cũ hơn → Test FAIL

### 4.7. Ví dụ 4: Test Model có Data cho Date cụ thể

**File: `macros/test_has_data_for_date.sql`**
```sql
{% test has_data_for_date(model, date_column, target_date) %}

WITH data_check AS (
  SELECT COUNT(*) AS row_count
  FROM {{ model }}
  WHERE {{ date_column }} = '{{ target_date }}'
)
SELECT
  'No data found for date {{ target_date }}' AS error_message
FROM data_check
WHERE row_count = 0

{% endtest %}
```

**Sử dụng:**
```yaml
models:
  - name: jobs
    data_tests:
      - has_data_for_date:
          date_column: scraped_date
          target_date: '2025-10-01'
```

### 4.8. Ví dụ 5: Test Row Count trong Range

**File: `macros/test_row_count_in_range.sql`**
```sql
{% test row_count_in_range(model, min_rows=1, max_rows=1000000) %}

WITH row_count AS (
  SELECT COUNT(*) AS total
  FROM {{ model }}
)
SELECT *
FROM row_count
WHERE total < {{ min_rows }}
   OR total > {{ max_rows }}

{% endtest %}
```

**Sử dụng:**
```yaml
models:
  - name: stg_jobs
    data_tests:
      - row_count_in_range:
          min_rows: 100
          max_rows: 50000
```

### 4.9. Ví dụ 6: Test Composite Uniqueness

**File: `macros/test_unique_combination.sql`**
```sql
{% test unique_combination(model, combination_of_columns) %}

SELECT
  {{ combination_of_columns | join(', ') }},
  COUNT(*) AS occurrences
FROM {{ model }}
GROUP BY {{ combination_of_columns | join(', ') }}
HAVING COUNT(*) > 1

{% endtest %}
```

**Sử dụng:**
```yaml
models:
  - name: stg_jobs
    data_tests:
      - unique_combination:
          combination_of_columns: ['job_url', 'scraped_date']
```

**Giải thích:**
- Test kiểm tra kết hợp `(job_url, scraped_date)` là unique
- Nếu có kết hợp nào xuất hiện >1 lần → Test FAIL

---

## 5. Best Practices

### 5.1. Khi nào dùng Singular vs Generic Tests?

| Trường hợp | Loại Test |
|------------|-----------|
| Logic đơn giản, tái sử dụng nhiều | **Generic Test** |
| Logic phức tạp, chỉ dùng 1 lần | **Singular Test** |
| Kiểm tra column (unique, not_null, format) | **Generic Test** |
| Kiểm tra business logic giữa nhiều models | **Singular Test** |
| Kiểm tra tồn tại data cho ngày cụ thể | **Singular Test** (hoặc Generic với params) |

### 5.2. Test Organization

```
dbt_crawjob/
├── macros/
│   ├── test_is_positive.sql
│   ├── test_valid_url.sql
│   ├── test_is_recent.sql
│   └── test_row_count_in_range.sql
├── tests/
│   ├── exist_today.sql
│   ├── no_duplicate_urls.sql
│   └── schema.yml
├── models/
│   ├── bronze/
│   │   └── schema.yml          # Generic tests for bronze
│   ├── silver/
│   │   └── schema.yml          # Generic tests for silver
│   └── gold/
│       └── schema.yml          # Generic tests for gold
```

### 5.3. Naming Conventions

| Type | Prefix | Ví dụ |
|------|--------|-------|
| **Singular Test** | `test_` (không bắt buộc) | `exist_today.sql`, `no_future_dates.sql` |
| **Generic Test Macro** | `test_` (bắt buộc) | `test_is_positive.sql`, `test_valid_url.sql` |

### 5.4. Test Levels

#### **Column-level Tests**
```yaml
columns:
  - name: job_url
    data_tests:
      - unique
      - not_null
      - valid_url
```

#### **Model-level Tests**
```yaml
models:
  - name: stg_jobs
    data_tests:
      - dbt_utils.expression_is_true:
          expression: "salary IS NOT NULL OR job_type = 'Volunteer'"
      - row_count_in_range:
          min_rows: 10
```

### 5.5. Severity Strategy

```yaml
models:
  - name: stg_jobs
    columns:
      - name: job_url
        data_tests:
          - unique:
              severity: error      # ← Critical: Phải PASS
          - not_null:
              severity: error
      
      - name: salary
        data_tests:
          - not_null:
              severity: warn       # ← Nice-to-have: có thể NULL
      
      - name: benefits
        data_tests:
          - not_null:
              severity: warn
```

### 5.6. Store Test Failures

Config để lưu failed rows vào table (để debug):

```yaml
tests:
  +store_failures: true
  +schema: test_failures
```

**Chạy test và lưu failures:**
```bash
dbt test --store-failures --profiles-dir .
```

→ Failed rows được lưu vào schema `test_failures` với tên table `<test_name>.sql`

---

## 6. Ví dụ Thực tế cho Project CrawlJob

### 6.1. Custom Generic Tests cho CrawlJob

#### **Test 1: Valid Source Site**

**File: `macros/test_valid_source_site.sql`**
```sql
{% test valid_source_site(model, column_name) %}

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

#### **Test 2: Salary Contains Currency**

**File: `macros/test_salary_has_currency.sql`**
```sql
{% test salary_has_currency(model, column_name) %}

SELECT *
FROM {{ model }}
WHERE {{ column_name }} IS NOT NULL
  AND {{ column_name }} != 'Negotiate'
  AND NOT (
    {{ column_name }} LIKE '%VND%'
    OR {{ column_name }} LIKE '%USD%'
    OR {{ column_name }} LIKE '%$%'
  )

{% endtest %}
```

#### **Test 3: Deadline After Scraped Date**

**File: `macros/test_deadline_after_scraped.sql`**
```sql
{% test deadline_after_scraped(model, deadline_column, scraped_column) %}

SELECT *
FROM {{ model }}
WHERE {{ deadline_column }} IS NOT NULL
  AND {{ scraped_column }} IS NOT NULL
  AND {{ deadline_column }} < {{ scraped_column }}

{% endtest %}
```

### 6.2. Áp dụng Tests cho Models

#### **Bronze Layer: `models/bronze/schema.yml`**
```yaml
version: 2

models:
  - name: jobs
    description: "Raw job data synced from PostgreSQL"
    data_tests:
      - row_count_in_range:
          min_rows: 10
          max_rows: 100000
    
    columns:
      - name: job_url
        description: "Unique URL of the job posting"
        data_tests:
          - unique
          - not_null
          - valid_url
      
      - name: source_site
        description: "Source website name"
        data_tests:
          - not_null
          - valid_source_site
      
      - name: scraped_at
        description: "Timestamp when data was scraped"
        data_tests:
          - not_null
          - is_recent:
              days_ago: 7
      
      - name: job_deadline
        description: "Job application deadline"
        data_tests:
          - deadline_after_scraped:
              deadline_column: job_deadline
              scraped_column: scraped_at
```

#### **Silver Layer: `models/silver/schema.yml`**
```yaml
version: 2

models:
  - name: stg_jobs
    description: "Staging layer for jobs with normalized data"
    data_tests:
      - unique_combination:
          combination_of_columns: ['job_url', 'scraped_date']
    
    columns:
      - name: job_url
        data_tests:
          - unique
          - not_null
          - valid_url
      
      - name: company_name
        data_tests:
          - not_null
      
      - name: salary
        data_tests:
          - salary_has_currency:
              severity: warn
      
      - name: scraped_date
        data_tests:
          - not_null
```

#### **Gold Layer: `models/gold/schema.yml`**
```yaml
version: 2

models:
  - name: dim_company
    columns:
      - name: company_name
        data_tests:
          - unique
          - not_null
      
      - name: total_jobs
        data_tests:
          - is_positive
  
  - name: fct_jobs
    columns:
      - name: company_name
        data_tests:
          - relationships:
              to: ref('dim_company')
              field: company_name
```

### 6.3. Singular Tests cho CrawlJob

#### **File: `tests/data_freshness_check.sql`**
```sql
-- Test FAILS if no data was scraped in the last 24 hours
SELECT
    'No data scraped in last 24 hours' AS error_message,
    MAX(scraped_at) AS last_scraped_at
FROM {{ source('bronze', 'jobs') }}
HAVING MAX(scraped_at) < CURRENT_TIMESTAMP - INTERVAL '24 hours'
```

#### **File: `tests/no_duplicate_job_urls.sql`**
```sql
-- Test FAILS if same job_url appears multiple times on same date
SELECT
    job_url,
    scraped_date,
    COUNT(*) AS occurrences
FROM {{ ref('stg_jobs') }}
GROUP BY job_url, scraped_date
HAVING COUNT(*) > 1
```

#### **File: `tests/all_spiders_ran.sql`**
```sql
-- Test FAILS if not all 10 spiders have data for today
WITH spider_count AS (
  SELECT COUNT(DISTINCT source_site) AS total_spiders
  FROM {{ source('bronze', 'jobs') }}
  WHERE scraped_date = CURRENT_DATE
)
SELECT
  'Expected 10 spiders, found ' || total_spiders AS error_message
FROM spider_count
WHERE total_spiders < 10
```

### 6.4. Chạy Tests

```bash
# Chạy tất cả tests
dbt test --profiles-dir .

# Chạy tests cho bronze layer
dbt test --profiles-dir . --select models/bronze

# Chạy tests cho silver layer
dbt test --profiles-dir . --select models/silver

# Chạy chỉ generic tests
dbt test --profiles-dir . --select test_type:generic

# Chạy chỉ singular tests
dbt test --profiles-dir . --select test_type:singular

# Chạy test cụ thể
dbt test --profiles-dir . --select unique_jobs_job_url

# Chạy và lưu failures
dbt test --profiles-dir . --store-failures
```

### 6.5. Test trong CI/CD (Airflow DAG)

```python
# airflow/dags/crawljob_pipeline.py

dbt_test_bronze = BashOperator(
    task_id='dbt_test_bronze',
    bash_command='cd /path/to/dbt_crawjob && dbt test --profiles-dir . --select models/bronze'
)

dbt_test_silver = BashOperator(
    task_id='dbt_test_silver',
    bash_command='cd /path/to/dbt_crawjob && dbt test --profiles-dir . --select models/silver'
)

dbt_test_gold = BashOperator(
    task_id='dbt_test_gold',
    bash_command='cd /path/to/dbt_crawjob && dbt test --profiles-dir . --select models/gold'
)

# DAG flow
dbt_run_bronze >> dbt_test_bronze >> dbt_run_silver >> dbt_test_silver >> dbt_run_gold >> dbt_test_gold
```

---

## 7. Tổng kết

### ✅ Checklist

- [ ] Bronze models có tests: unique, not_null, valid URLs
- [ ] Silver models có tests: composite uniqueness, data freshness
- [ ] Gold models có tests: relationships (foreign keys), positive counts
- [ ] Custom generic tests cho business logic (valid source sites, salary format, etc.)
- [ ] Singular tests cho critical checks (data exists today, all spiders ran)
- [ ] Severity levels được set đúng (error vs warn)
- [ ] Tests được integrate vào Airflow DAG

### 🎯 Key Takeaways

1. **Singular Tests**: Định nghĩa trong `tests/*.sql`, dùng cho logic phức tạp, one-time
2. **Generic Tests**: Định nghĩa trong `macros/test_*.sql`, tái sử dụng nhiều lần
3. **Macro template**: `{% test test_name(model, column) %} ... {% endtest %}`
4. **Test PASS**: Query returns 0 rows
5. **Test FAIL**: Query returns >0 rows
6. **Severity**: `error` (fail build) vs `warn` (chỉ warning)
7. **Custom tests**: Viết trong `macros/`, sử dụng trong `schema.yml`

### 📚 Resources

- [dbt Docs - Tests](https://docs.getdbt.com/docs/build/data-tests)
- [dbt Docs - Custom Generic Tests](https://docs.getdbt.com/best-practices/writing-custom-generic-tests)
- [dbt Utils Package](https://hub.getdbt.com/dbt-labs/dbt_utils/latest/)
- [dbt Expectations Package](https://hub.getdbt.com/calogica/dbt_expectations/latest/)
