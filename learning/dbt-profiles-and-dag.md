# dbt Profiles và DAG Dependencies - Hướng dẫn Chi tiết

## 📚 Mục lục
1. [dbt Profiles - Quản lý Kết nối Database](#1-dbt-profiles---quản-lý-kết-nối-database)
2. [DAG Dependencies - Cách dbt Sắp xếp Thứ tự Chạy Models](#2-dag-dependencies---cách-dbt-sắp-xếp-thứ-tự-chạy-models)
3. [Best Practices](#3-best-practices)
4. [Troubleshooting](#4-troubleshooting)

---

## 1. dbt Profiles - Quản lý Kết nối Database

### 1.1. Profiles.yml là gì?

**Profiles.yml** là file cấu hình chứa thông tin **kết nối đến data warehouse** (credentials, connection strings). File này **KHÔNG NÊN commit vào Git** nếu chứa thông tin nhạy cảm (passwords).

### 1.2. Vị trí mặc định của profiles.yml

**Theo mặc định**, dbt tìm `profiles.yml` ở:

| OS | Đường dẫn |
|----|-----------|
| **Windows** | `C:\Users\<username>\.dbt\profiles.yml` |
| **macOS** | `~/.dbt/profiles.yml` |
| **Linux** | `~/.dbt/profiles.yml` |

### 1.3. Override vị trí profiles.yml

Có 2 cách để dbt tìm `profiles.yml` ở vị trí khác:

#### **Cách 1: Sử dụng flag `--profiles-dir`**
```bash
dbt run --profiles-dir .
dbt run --profiles-dir /path/to/profiles
```

**Ý nghĩa:**
- `--profiles-dir .` → Tìm `profiles.yml` ở **thư mục hiện tại**
- Hữu ích khi đưa `profiles.yml` vào Git (với hardcoded paths hoặc env vars)

#### **Cách 2: Sử dụng biến môi trường `DBT_PROFILES_DIR`**
```bash
# Windows (CMD)
set DBT_PROFILES_DIR=D:\Practice\Scrapy\CrawlJob\dbt_crawjob
dbt run

# Windows (PowerShell)
$env:DBT_PROFILES_DIR="D:\Practice\Scrapy\CrawlJob\dbt_crawjob"
dbt run

# Linux/macOS
export DBT_PROFILES_DIR=/path/to/dbt_project
dbt run
```

**Lợi ích:** Không cần thêm `--profiles-dir` mỗi lần chạy command.

### 1.4. Cấu trúc profiles.yml

#### **Ví dụ cơ bản (DuckDB):**
```yaml
crawljob:                          # Profile name (phải khớp với dbt_project.yml)
  target: dev                       # Target mặc định
  outputs:
    dev:                            # Development environment
      type: duckdb                  # Adapter type
      path: "D:\\Practice\\Scrapy\\CrawlJob\\DuckDB\\warehouse.duckdb"
    
    prod:                           # Production environment
      type: duckdb
      path: "/prod/warehouse.duckdb"
```

#### **Ví dụ với PostgreSQL:**
```yaml
my_project:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      port: 5432
      user: myuser
      password: mypassword          # ⚠️ Không commit vào Git!
      dbname: dev_db
      schema: analytics
      threads: 4
    
    prod:
      type: postgres
      host: prod-db.example.com
      port: 5432
      user: "{{ env_var('PROD_DB_USER') }}"          # ✅ Dùng env vars
      password: "{{ env_var('PROD_DB_PASSWORD') }}"
      dbname: prod_db
      schema: analytics
      threads: 8
```

#### **Ví dụ với Snowflake:**
```yaml
snowflake_project:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: my_account
      user: dev_user
      password: "{{ env_var('SNOWFLAKE_PASSWORD') }}"
      role: DEV_ROLE
      database: DEV_DB
      warehouse: DEV_WH
      schema: analytics
      threads: 4
```

### 1.5. Liên kết profiles.yml với dbt_project.yml

Trong `dbt_project.yml`, phải chỉ định profile name:

```yaml
name: 'crawljob'
version: '1.0.0'
profile: 'crawljob'        # ← Phải khớp với tên profile trong profiles.yml
```

### 1.6. Switching giữa Environments (dev/prod)

```bash
# Chạy với target dev (mặc định)
dbt run --profiles-dir .

# Chạy với target prod
dbt run --profiles-dir . --target prod

# Debug connection
dbt debug --profiles-dir . --target dev
```

### 1.7. Best Practices cho Profiles

| ✅ **NÊN** | ❌ **KHÔNG NÊN** |
|----------|---------------|
| Dùng `env_var()` cho credentials | Hard-code passwords vào profiles.yml |
| Có targets riêng cho dev/prod | Dùng chung 1 target cho mọi môi trường |
| `.gitignore` profiles.yml nếu có sensitive data | Commit passwords vào Git |
| Dùng `--profiles-dir .` cho CI/CD | Rely on `~/.dbt/` trong CI |
| Validate connection với `dbt debug` | Chạy `dbt run` mà không kiểm tra connection trước |

### 1.8. Sử dụng Environment Variables

**Trong profiles.yml:**
```yaml
crawljob:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: "{{ env_var('DUCKDB_PATH') }}"  # Đọc từ env var
```

**Set env var trước khi chạy dbt:**
```bash
# Windows CMD
set DUCKDB_PATH=D:\Practice\Scrapy\CrawlJob\DuckDB\warehouse.duckdb
dbt run --profiles-dir .

# Linux/macOS
export DUCKDB_PATH=/path/to/warehouse.duckdb
dbt run --profiles-dir .
```

⚠️ **LƯU Ý:** DuckDB adapter có thể không hỗ trợ env_var() tốt, nên dùng hardcoded path trong profiles.yml.

---

## 2. DAG Dependencies - Cách dbt Sắp xếp Thứ tự Chạy Models

### 2.1. DAG (Directed Acyclic Graph) là gì?

**DAG** là **đồ thị có hướng không có chu trình**, dùng để biểu diễn **dependencies** giữa các models.

```
Source (bronze.jobs)
    ↓
Model A (silver.stg_jobs)
    ↓         ↓
Model B      Model C (gold.dim_company, gold.fct_jobs)
```

**Đặc điểm:**
- **Directed (Có hướng):** A → B nghĩa là B phụ thuộc A
- **Acyclic (Không chu trình):** Không có vòng lặp (A → B → A)

### 2.2. Cách dbt Phát hiện Dependencies

dbt **TỰ ĐỘNG** phát hiện dependencies bằng cách parse **Jinja functions** trong SQL:

#### **Hàm 1: `{{ source('schema', 'table') }}`**

Tham chiếu đến **external table** (đã tồn tại trong warehouse, không do dbt tạo).

**Ví dụ:**
```yaml
# models/sources.yml
version: 2
sources:
  - name: bronze               # Source name
    schema: bronze             # Schema trong warehouse
    tables:
      - name: jobs             # Table name
```

```sql
-- models/silver/stg_jobs.sql
SELECT *
FROM {{ source('bronze', 'jobs') }}  -- ← Compile thành: bronze.jobs
```

**Compile thành SQL:**
```sql
SELECT * FROM bronze.jobs
```

#### **Hàm 2: `{{ ref('model_name') }}`**

Tham chiếu đến **model khác** trong dbt project.

**Ví dụ:**
```sql
-- models/gold/fct_jobs.sql
SELECT *
FROM {{ ref('stg_jobs') }}  -- ← Tham chiếu model stg_jobs
```

**Compile thành SQL:**
```sql
SELECT * FROM silver.stg_jobs
```

**Dependencies:**
```
stg_jobs (silver) → fct_jobs (gold)
```

#### **Hàm 3: `{{ this }}`**

Tham chiếu đến **chính model hiện tại** (dùng trong incremental models).

**Ví dụ:**
```sql
-- models/silver/stg_jobs.sql
{% if is_incremental() %}
WHERE scraped_at > (SELECT MAX(scraped_at) FROM {{ this }})
{% endif %}
```

**Compile thành SQL:**
```sql
WHERE scraped_at > (SELECT MAX(scraped_at) FROM silver.stg_jobs)
```

### 2.3. Ví dụ: Build DAG cho Project CrawlJob

#### **Step 1: Define Sources**
```yaml
# models/sources.yml
version: 2
sources:
  - name: bronze
    schema: bronze
    tables:
      - name: jobs  # Level 0 - External table
```

#### **Step 2: Silver Layer Model**
```sql
-- models/silver/stg_jobs.sql
{{ config(
  materialized='incremental',
  schema='silver',
  unique_key=['job_url','scraped_date']
) }}

SELECT
  job_url,
  TRIM(job_title) AS job_title,
  LOWER(company_name) AS company_name,
  salary,
  location,
  scraped_at
FROM {{ source('bronze','jobs') }}  -- ← Depends on bronze.jobs

{% if is_incremental() %}
WHERE scraped_at > (SELECT MAX(scraped_at) FROM {{ this }})
{% endif %}
```

**Dependencies:** `bronze.jobs → stg_jobs`

#### **Step 3: Gold Layer Models**
```sql
-- models/gold/dim_company.sql
{{ config(
  materialized='table',
  schema='gold'
) }}

SELECT DISTINCT
  company_name,
  COUNT(*) AS total_jobs
FROM {{ ref('stg_jobs') }}  -- ← Depends on stg_jobs
GROUP BY company_name
```

```sql
-- models/gold/fct_jobs.sql
{{ config(
  materialized='incremental',
  schema='gold',
  unique_key='job_url'
) }}

SELECT
  job_url,
  job_title,
  company_name,
  salary,
  location
FROM {{ ref('stg_jobs') }}  -- ← Depends on stg_jobs
```

**Dependencies:**
```
bronze.jobs (source)
    ↓
stg_jobs (silver)
    ↓              ↓
dim_company    fct_jobs (gold)
```

### 2.4. dbt Execution Order (Topological Sort)

Khi chạy `dbt run`, dbt sẽ:

#### **Step 1: Parse tất cả models**
- Đọc tất cả `.sql`, `.yml` files
- Tìm `{{ source() }}`, `{{ ref() }}` trong SQL

#### **Step 2: Build DAG**
```
Level 0: bronze.jobs (source - skip)
Level 1: stg_jobs (depends on bronze.jobs)
Level 2: dim_company, fct_jobs (depends on stg_jobs)
```

#### **Step 3: Topological Sort**
Sắp xếp thứ tự execute từ upstream → downstream:
```
1. stg_jobs (run first)
2. dim_company, fct_jobs (run in parallel - cùng level)
```

#### **Step 4: Execute**
```sql
-- 1. CREATE silver.stg_jobs
CREATE TABLE silver.stg_jobs AS
SELECT ... FROM bronze.jobs;

-- 2. CREATE gold.dim_company (parallel)
CREATE TABLE gold.dim_company AS
SELECT ... FROM silver.stg_jobs;

-- 3. CREATE gold.fct_jobs (parallel)
CREATE TABLE gold.fct_jobs AS
SELECT ... FROM silver.stg_jobs;
```

### 2.5. Visualize DAG

#### **Cách 1: dbt Docs**
```bash
cd dbt_crawjob
dbt docs generate --profiles-dir .
dbt docs serve
```

→ Mở browser tại `http://localhost:8080`, xem **Lineage Graph**.

#### **Cách 2: dbt ls (List Resources)**
```bash
# Xem tất cả models
dbt ls --profiles-dir .

# Xem dependencies của stg_jobs
dbt ls --select +stg_jobs      # Upstream (models mà stg_jobs phụ thuộc)
dbt ls --select stg_jobs+      # Downstream (models phụ thuộc stg_jobs)
dbt ls --select +stg_jobs+     # Both upstream & downstream

# Xem graph structure
dbt ls --select +stg_jobs+ --output json
```

### 2.6. Node Selection Syntax

dbt cung cấp **powerful syntax** để chạy subset models:

| Syntax | Ý nghĩa | Ví dụ |
|--------|---------|-------|
| `dbt run -s model_name` | Chỉ chạy 1 model | `dbt run -s stg_jobs` |
| `dbt run -s +model_name` | Chạy model + tất cả upstream | `dbt run -s +fct_jobs` |
| `dbt run -s model_name+` | Chạy model + tất cả downstream | `dbt run -s stg_jobs+` |
| `dbt run -s +model_name+` | Chạy model + upstream + downstream | `dbt run -s +stg_jobs+` |
| `dbt run -s tag:daily` | Chạy models có tag `daily` | `dbt run -s tag:daily` |
| `dbt run -s path:models/silver` | Chạy models trong folder | `dbt run -s path:models/silver` |
| `dbt run -s @model_name` | Chạy model + parents (1 level up) | `dbt run -s @fct_jobs` |
| `dbt run --exclude model_name` | Chạy tất cả trừ model | `dbt run --exclude stg_jobs` |

**Ví dụ thực tế:**
```bash
# Chạy chỉ silver layer
dbt run -s path:models/silver --profiles-dir .

# Chạy stg_jobs và tất cả models downstream (gold)
dbt run -s stg_jobs+ --profiles-dir .

# Chạy tất cả models cần cho fct_jobs (upstream + chính nó)
dbt run -s +fct_jobs --profiles-dir .

# Chạy models có tag "hourly"
dbt run -s tag:hourly --profiles-dir .
```

### 2.7. Parallel Execution

dbt chạy models **song song** nếu chúng ở **cùng level** trong DAG.

**Config threads trong profiles.yml:**
```yaml
crawljob:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: "warehouse.duckdb"
      threads: 4  # ← Số lượng models chạy song song
```

**Ví dụ:**
```
stg_jobs (run first - 1 thread)
    ↓
dim_company, fct_jobs, dim_location, agg_daily (run parallel - 4 threads)
```

---

## 3. Best Practices

### 3.1. Naming Conventions

| Layer | Prefix | Schema | Ví dụ |
|-------|--------|--------|-------|
| **Staging** | `stg_` | `silver` | `stg_jobs`, `stg_companies` |
| **Intermediate** | `int_` | `silver` | `int_job_enriched` |
| **Marts (Dimensions)** | `dim_` | `gold` | `dim_company`, `dim_location` |
| **Marts (Facts)** | `fct_` | `gold` | `fct_jobs`, `fct_applications` |
| **Aggregates** | `agg_` | `gold` | `agg_jobs_daily` |

### 3.2. Source() vs Ref()

| Hàm | Khi nào dùng | Ví dụ |
|-----|-------------|--------|
| `{{ source() }}` | External tables (không do dbt tạo) | `{{ source('bronze','jobs') }}` |
| `{{ ref() }}` | Models trong dbt project | `{{ ref('stg_jobs') }}` |

**❌ KHÔNG BAO GIỜ hard-code table names:**
```sql
-- ❌ SAI
SELECT * FROM bronze.jobs
SELECT * FROM silver.stg_jobs

-- ✅ ĐÚNG
SELECT * FROM {{ source('bronze','jobs') }}
SELECT * FROM {{ ref('stg_jobs') }}
```

**Lý do:**
- dbt không track dependencies nếu hard-code
- Không refactor được khi đổi schema/table names

### 3.3. Incremental Models Best Practices

```sql
{{ config(
  materialized='incremental',
  unique_key=['job_url', 'scraped_date'],  -- ← Composite key
  incremental_strategy='merge'              -- ← Merge (upsert) hoặc append
) }}

SELECT
  job_url,
  job_title,
  scraped_at
FROM {{ source('bronze','jobs') }}

{% if is_incremental() %}
-- ✅ Filter chỉ lấy dữ liệu mới
WHERE scraped_at > (SELECT COALESCE(MAX(scraped_at), '1970-01-01') FROM {{ this }})
{% endif %}
```

**Chiến lược incremental:**
- **`merge`**: Upsert (update existing + insert new) - **Recommend cho most cases**
- **`append`**: Chỉ insert mới (không update) - **Dùng cho immutable data**
- **`delete+insert`**: Xóa partition cũ + insert mới - **Dùng cho partitioned tables**

### 3.4. Schema Organization

```
models/
├── sources.yml           # Define all sources
├── bronze/
│   └── schema.yml        # Tests cho bronze tables
├── silver/
│   ├── stg_jobs.sql
│   ├── stg_companies.sql
│   └── schema.yml        # Tests + descriptions
├── gold/
│   ├── dim_company.sql
│   ├── fct_jobs.sql
│   ├── agg_jobs_daily.sql
│   └── schema.yml
```

### 3.5. Tags và Meta

Dùng tags để organize và select models:

```yaml
# models/silver/schema.yml
version: 2
models:
  - name: stg_jobs
    description: "Staging layer for jobs"
    meta:
      owner: "data_team"
      priority: "high"
    config:
      tags: ["daily", "core"]
    columns:
      - name: job_url
        tests:
          - unique
          - not_null
```

**Chạy models theo tags:**
```bash
dbt run -s tag:daily
dbt run -s tag:core
dbt test -s tag:daily
```

---

## 4. Troubleshooting

### 4.1. Lỗi: "Profile not found"

**Lỗi:**
```
Runtime Error
  Could not find profile named 'crawljob'
```

**Nguyên nhân:**
- `profiles.yml` không tồn tại hoặc ở sai vị trí
- Profile name trong `dbt_project.yml` không khớp với `profiles.yml`

**Giải pháp:**
```bash
# Kiểm tra profile
dbt debug --profiles-dir .

# Đảm bảo profile name khớp
# dbt_project.yml
profile: 'crawljob'

# profiles.yml
crawljob:  # ← Phải giống nhau
  target: dev
```

### 4.2. Lỗi: Circular Dependencies

**Lỗi:**
```
Compilation Error
  Found a cycle in the dependency graph: model_a → model_b → model_a
```

**Nguyên nhân:** Model A ref() Model B, và Model B ref() Model A.

**Giải pháp:** Refactor để break cycle:
```sql
-- Tạo model intermediate
-- models/intermediate/int_shared.sql
SELECT ... FROM {{ source('bronze','jobs') }}

-- models/model_a.sql
SELECT ... FROM {{ ref('int_shared') }}

-- models/model_b.sql
SELECT ... FROM {{ ref('int_shared') }}
```

### 4.3. Lỗi: Model không chạy đúng thứ tự

**Nguyên nhân:** Không dùng `{{ ref() }}` hoặc `{{ source() }}`.

**Giải pháp:**
```sql
-- ❌ SAI - dbt không biết dependency
SELECT * FROM silver.stg_jobs

-- ✅ ĐÚNG
SELECT * FROM {{ ref('stg_jobs') }}
```

### 4.4. Lỗi: DuckDB không đọc env_var()

**Lỗi:**
```
Database Error in model ...
  No such table: warehouse.duckdb
```

**Nguyên nhân:** DuckDB adapter không hỗ trợ env_var() trong path.

**Giải pháp:** Hardcode path trong profiles.yml:
```yaml
dev:
  type: duckdb
  path: "D:\\Practice\\Scrapy\\CrawlJob\\DuckDB\\warehouse.duckdb"  # ← Hardcoded
```

### 4.5. Lỗi: Incremental model không filter dữ liệu mới

**Lỗi:** Mỗi lần chạy `dbt run`, model incremental vẫn xử lý toàn bộ dữ liệu.

**Nguyên nhân:** Thiếu `{% if is_incremental() %}` filter.

**Giải pháp:**
```sql
{{ config(materialized='incremental') }}

SELECT * FROM {{ source('bronze','jobs') }}

{% if is_incremental() %}
-- ✅ Thêm filter
WHERE scraped_at > (SELECT MAX(scraped_at) FROM {{ this }})
{% endif %}
```

---

## 5. Tổng kết

### ✅ Checklist cho dbt Project

- [ ] `profiles.yml` đã cấu hình đúng với warehouse
- [ ] `dbt debug --profiles-dir .` chạy thành công
- [ ] Tất cả models dùng `{{ source() }}` và `{{ ref() }}`, không hard-code table names
- [ ] Incremental models có `{% if is_incremental() %}` filter
- [ ] Schema organization: bronze → silver → gold
- [ ] Tests được định nghĩa trong `schema.yml`
- [ ] DAG không có circular dependencies
- [ ] Tags được sử dụng cho scheduling (daily, hourly, etc.)

### 🎯 Key Takeaways

1. **Profiles.yml**: Quản lý kết nối database, dùng `--profiles-dir .` cho portability
2. **DAG**: dbt tự động phát hiện dependencies qua `{{ source() }}` và `{{ ref() }}`
3. **Execution Order**: Topological sort → upstream models chạy trước downstream
4. **Best Practices**: Luôn dùng `{{ ref() }}` và `{{ source() }}`, không hard-code table names
5. **Node Selection**: Dùng `-s`, `+`, tags để chạy subset models

### 📚 Resources

- [dbt Docs - Profiles](https://docs.getdbt.com/docs/core/connect-data-platform/profiles.yml)
- [dbt Docs - ref() and source()](https://docs.getdbt.com/reference/dbt-jinja-functions/ref)
- [dbt Docs - Node Selection](https://docs.getdbt.com/reference/node-selection/syntax)
- [dbt Docs - Incremental Models](https://docs.getdbt.com/docs/build/incremental-models)
- [dbt Best Practices Guide](https://docs.getdbt.com/guides/best-practices)
