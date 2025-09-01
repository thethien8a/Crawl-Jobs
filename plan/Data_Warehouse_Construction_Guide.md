# Cách Xây Dựng Data Warehouse Dựa Vào Dữ Liệu Job Hiện Có

## 🎯 **TỔNG QUAN**

**Dữ liệu hiện tại của bạn**: Raw job data từ 10 websites (JobsGO, TopCV, ITviec, v.v.)  
**Mục tiêu**: Xây dựng Data Warehouse để phân tích thị trường việc làm  
**Approach**: Kimball Dimensional Modeling (phù hợp cho project nhỏ-vừa)

---

## 🏗️ **QUY TRÌNH XÂY DỰNG DATA WAREHOUSE (7 BƯỚC)**

### **BƯỚC 1: PHÂN TÍCH BUSINESS REQUIREMENTS (1-2 tuần)**

#### **Câu hỏi business cần trả lời:**
```
📊 Analytics Questions:
- Xu hướng lương theo vị trí/thành phố?
- Skill nào đang hot nhất?
- Company nào tuyển nhiều nhất?
- Thị trường việc làm IT growth như thế nào?
- Job posting patterns theo thời gian?

👥 User Personas:
- Job seekers: "Tìm job phù hợp với skill"
- Recruiters: "Hiểu market trends"  
- Researchers: "Phân tích thị trường lao động"
```

#### **KPIs cần track:**
```
📈 Core Metrics:
- Số lượng job postings/tháng
- Average salary by location/role
- Top skills in demand
- Hiring velocity by company
- Job fulfillment rate
```

---

### **BƯỚC 2: DATA DISCOVERY & AUDIT (1 tuần)**

#### **Inventory dữ liệu hiện có:**
```
📋 Current Data Sources:
✅ 10 job websites (JobsGO, TopCV, ITviec, LinkedIn, etc.)
✅ 17+ fields per job (title, company, salary, location, description, etc.)
✅ SQL Server database với 10,000+ records
✅ Daily crawling automation

📊 Data Quality Assessment:
- Completeness: 85% jobs có đầy đủ title + company
- Accuracy: 90% salary format đúng
- Consistency: 70% location cần standardize
- Timeliness: Daily updates
```

#### **Gaps cần fill:**
```
❌ Missing Data:
- Company size/industry classification
- Job posting duration (how long posted)
- Application success rates
- Skill tags standardization
- Geographic coordinates for locations
```

---

### **BƯỚC 3: DIMENSIONAL MODELING (2 tuần)**

#### **Business Process Analysis:**
```
🔍 Core Business Process: "Job Market Analysis"

Key business events:
1. Job được post lên website
2. Job được crawl vào system
3. Job được search bởi users
4. Job expired/fulfilled
```

#### **Dimensional Model Design:**

##### **FACT TABLE: fact_job_postings**
```sql
-- Central fact table chứa metrics
CREATE TABLE fact_job_postings (
    job_posting_key BIGINT PRIMARY KEY,
    
    -- Foreign keys to dimensions
    job_key INT,           -- Link to dim_job
    company_key INT,       -- Link to dim_company  
    location_key INT,      -- Link to dim_location
    date_key INT,          -- Link to dim_date
    source_key INT,        -- Link to dim_source
    
    -- Additive measures (có thể SUM)
    view_count INT DEFAULT 0,
    application_count INT DEFAULT 0,
    days_posted INT,
    
    -- Semi-additive measures (AVG, không SUM)
    salary_min DECIMAL(12,2),
    salary_max DECIMAL(12,2),
    salary_avg DECIMAL(12,2),
    
    -- Non-additive measures (chỉ display)
    posting_status VARCHAR(50),  -- 'active', 'expired', 'filled'
    
    -- Timestamps
    posted_date DATE,
    crawled_date DATE,
    updated_date DATE
);
```

##### **DIMENSION TABLES:**

**dim_job (Job Information)**
```sql
CREATE TABLE dim_job (
    job_key INT PRIMARY KEY,
    
    -- Natural key
    job_id VARCHAR(100),  -- From source website
    
    -- Job attributes
    job_title VARCHAR(500),
    job_title_standardized VARCHAR(200),  -- "Senior Python Developer"
    job_level VARCHAR(50),                -- "Senior", "Junior", "Mid"
    job_category VARCHAR(100),            -- "Software Engineering", "Data Science"
    
    -- Requirements
    experience_required VARCHAR(100),
    education_required VARCHAR(100),
    skills_required TEXT,                 -- JSON array of skills
    
    -- Job details
    job_type VARCHAR(50),                 -- "Full-time", "Remote", "Contract"
    job_description TEXT,
    benefits TEXT,
    
    -- SCD Type 2 fields
    effective_date DATE,
    expiry_date DATE,
    is_current BIT DEFAULT 1
);
```

**dim_company (Company Information)**
```sql
CREATE TABLE dim_company (
    company_key INT PRIMARY KEY,
    
    -- Natural key
    company_name VARCHAR(500),
    company_name_standardized VARCHAR(200),  -- "FPT Software"
    
    -- Company attributes
    company_size VARCHAR(50),                -- "1-50", "51-200", "200+"
    industry VARCHAR(100),                   -- "Technology", "Finance"
    company_type VARCHAR(50),                -- "Startup", "Enterprise", "MNC"
    
    -- Location
    headquarters_location VARCHAR(200),
    
    -- Metadata
    first_seen_date DATE,
    last_updated DATE,
    is_active BIT DEFAULT 1
);
```

**dim_location (Geographic Information)**
```sql
CREATE TABLE dim_location (
    location_key INT PRIMARY KEY,
    
    -- Geographic hierarchy
    location_raw VARCHAR(200),           -- Original text
    city VARCHAR(100),                   -- "Ho Chi Minh City"
    province VARCHAR(100),               -- "Ho Chi Minh"
    region VARCHAR(50),                  -- "South", "North", "Central"
    country VARCHAR(50) DEFAULT 'Vietnam',
    
    -- Coordinates for mapping
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Economic data (future enhancement)
    cost_of_living_index DECIMAL(5,2),
    avg_rent DECIMAL(10,2)
);
```

**dim_date (Time Dimension)**
```sql
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,            -- YYYYMMDD format
    
    -- Date attributes
    full_date DATE,
    year INT,
    quarter INT,
    month INT,
    month_name VARCHAR(20),
    week_of_year INT,
    day_of_month INT,
    day_of_week INT,
    day_name VARCHAR(20),
    
    -- Business calendar
    is_weekend BIT,
    is_holiday BIT,
    is_business_day BIT,
    
    -- Fiscal calendar (if needed)
    fiscal_year INT,
    fiscal_quarter INT
);
```

**dim_source (Data Source Information)**
```sql
CREATE TABLE dim_source (
    source_key INT PRIMARY KEY,
    
    -- Source attributes
    source_name VARCHAR(100),            -- "TopCV", "ITviec"
    source_url VARCHAR(500),
    source_type VARCHAR(50),             -- "Job Board", "Company Site"
    source_category VARCHAR(50),         -- "General", "Tech-focused"
    
    -- Quality metrics
    data_quality_score DECIMAL(3,2),    -- 0.00 to 1.00
    update_frequency VARCHAR(50),        -- "Daily", "Real-time"
    reliability_score DECIMAL(3,2),
    
    -- Metadata
    first_crawled_date DATE,
    is_active BIT DEFAULT 1
);
```

---

### **BƯỚC 4: ETL DESIGN (2 tuần)**

#### **Extract (Extraction Strategy):**
```
🔄 Current State:
✅ Scrapy spiders đã extract từ 10 sources
✅ Raw data vào SQL Server

🎯 Enhancement:
- Add data lineage tracking
- Implement incremental extraction
- Error handling & retry logic
- Data validation at source
```

#### **Transform (Business Logic):**
```python
# Transformation Rules (Manual Definition)

def standardize_job_title(raw_title):
    """Standardize job titles theo business rules"""
    mappings = {
        'Sr. Developer': 'Senior Developer',
        'Jr. Developer': 'Junior Developer', 
        'Dev': 'Developer',
        'Eng': 'Engineer',
        'PM': 'Project Manager'
    }
    return mappings.get(raw_title, raw_title)

def parse_salary(salary_text):
    """Parse salary từ text thành numeric range"""
    # "15-20 triệu" → min: 15000000, max: 20000000
    # "Thỏa thuận" → min: NULL, max: NULL
    # "$1000-2000" → min: 1000, max: 2000 (USD)
    pass

def standardize_location(raw_location):
    """Standardize locations theo hierarchy"""
    mapping = {
        'HCM': 'Ho Chi Minh City',
        'Hà Nội': 'Hanoi',
        'Đà Nẵng': 'Da Nang'
    }
    return mapping.get(raw_location, raw_location)

def extract_skills(job_description, requirements):
    """Extract skill tags từ job description"""
    skills = ['Python', 'Java', 'React', 'SQL', 'AWS', 'Docker']
    found_skills = []
    for skill in skills:
        if skill.lower() in (job_description + requirements).lower():
            found_skills.append(skill)
    return found_skills
```

#### **Load (Loading Strategy):**
```sql
-- Slowly Changing Dimension Type 2
-- Example: Company information changes over time

-- When company changes industry:
-- Old record: effective_date='2024-01-01', expiry_date='2024-06-30', is_current=0
-- New record: effective_date='2024-07-01', expiry_date='9999-12-31', is_current=1

MERGE dim_company AS target
USING staging_company AS source
ON target.company_name = source.company_name AND target.is_current = 1
WHEN MATCHED AND target.industry != source.industry THEN
    UPDATE SET expiry_date = GETDATE(), is_current = 0
WHEN NOT MATCHED THEN
    INSERT (company_name, industry, effective_date, is_current)
    VALUES (source.company_name, source.industry, GETDATE(), 1);
```

---

### **BƯỚC 5: IMPLEMENTATION PHASES**

#### **Phase 1: Bronze Layer (Raw Data Warehouse)**
```
📥 Purpose: Store raw scraped data với minimal processing

Structure:
- jobs_bronze: Raw job data as-is
- crawl_log: ETL execution tracking  
- data_quality: Quality metrics per batch

Technology:
- SQLite cho development
- PostgreSQL cho production
```

#### **Phase 2: Silver Layer (Cleaned Data Warehouse)**  
```
🔧 Purpose: Cleaned, standardized, business-ready data

Transformations:
- Text normalization & cleaning
- Salary parsing & standardization  
- Location hierarchy mapping
- Duplicate removal
- Data validation

Technology:
- Pandas/Polars cho transformation
- DBT cho SQL transformations
- Great Expectations cho data quality
```

#### **Phase 3: Gold Layer (Analytics Data Marts)**
```
📊 Purpose: Pre-aggregated data cho specific use cases

Data Marts:
- job_market_trends: Monthly aggregations
- salary_analysis: Salary benchmarks
- skill_demand: Skill popularity trends
- company_insights: Hiring patterns

Technology:  
- Parquet files cho analytics
- Apache Spark cho big data processing
- ClickHouse cho OLAP queries
```

---

### **BƯỚC 6: AUTOMATION STRATEGY**

#### **Level 1: Basic Automation (Tuần 1-2)**
```bash
# Cron job đơn giản
# /etc/crontab
0 2 * * * cd /path/to/project && python etl/bronze_pipeline.py
0 4 * * * cd /path/to/project && python etl/silver_pipeline.py  
0 6 * * * cd /path/to/project && python etl/gold_pipeline.py
```

#### **Level 2: Orchestration (Tuần 3-6)**
```python
# Apache Airflow DAG
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

dag = DAG(
    'job_data_warehouse_pipeline',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1)
)

bronze_task = PythonOperator(
    task_id='bronze_etl',
    python_callable=run_bronze_pipeline,
    dag=dag
)

silver_task = PythonOperator(
    task_id='silver_etl', 
    python_callable=run_silver_pipeline,
    dag=dag
)

# Dependencies
bronze_task >> silver_task >> gold_task
```

#### **Level 3: Production Automation (Tuần 7-10)**
```yaml
# Docker Compose cho full automation
version: '3.8'
services:
  airflow-webserver:
    image: apache/airflow:2.5.0
    environment:
      - AIRFLOW__CORE__EXECUTOR=LocalExecutor
    volumes:
      - ./dags:/opt/airflow/dags
      - ./data:/opt/airflow/data
  
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: data_warehouse
      
  redis:
    image: redis:6
    
  monitoring:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

---

### **BƯỚC 7: MONITORING & MAINTENANCE**

#### **Data Quality Monitoring:**
```python
# Great Expectations cho data validation
import great_expectations as ge

def validate_job_data(df):
    """Validate job data quality"""
    suite = ge.DataContext().create_expectation_suite("job_validation")
    
    # Business rules
    suite.expect_column_to_not_be_null("job_title")
    suite.expect_column_to_not_be_null("company_name")
    suite.expect_column_values_to_be_in_set("source_site", 
        ["topcv.vn", "itviec.com", "jobsgo.vn"])
    suite.expect_column_values_to_match_regex("salary", 
        r"^\d+-\d+ triệu|Thỏa thuận|Competitive$")
    
    # Run validation
    results = df.validate(expectation_suite=suite)
    return results
```

#### **Pipeline Monitoring:**
```python
def monitor_pipeline_health():
    """Monitor ETL pipeline health"""
    metrics = {
        'last_run_time': get_last_etl_run(),
        'success_rate': calculate_success_rate(),
        'data_freshness': check_data_freshness(),
        'record_count': get_daily_record_count(),
        'quality_score': calculate_quality_score()
    }
    
    # Alert if issues
    if metrics['success_rate'] < 0.95:
        send_alert("ETL success rate below threshold")
    
    return metrics
```

---

## 🎯 **DIMENSIONAL MODEL CHO JOB DATA**

### **Star Schema Design:**

```
                    dim_date
                        |
                        |
dim_job -------- fact_job_postings -------- dim_company
                        |
                        |
                   dim_location
                        |
                   dim_source
```

### **Business Questions → SQL Queries:**

#### **"Top 10 companies tuyển nhiều nhất tháng này"**
```sql
SELECT 
    c.company_name,
    COUNT(*) as job_count
FROM fact_job_postings f
JOIN dim_company c ON f.company_key = c.company_key
JOIN dim_date d ON f.date_key = d.date_key
WHERE d.year = 2024 AND d.month = 12
GROUP BY c.company_name
ORDER BY job_count DESC
LIMIT 10;
```

#### **"Mức lương trung bình theo thành phố"**
```sql
SELECT 
    l.city,
    AVG(f.salary_avg) as avg_salary,
    COUNT(*) as job_count
FROM fact_job_postings f
JOIN dim_location l ON f.location_key = l.location_key
WHERE f.salary_avg IS NOT NULL
GROUP BY l.city
ORDER BY avg_salary DESC;
```

#### **"Skill demand trends theo thời gian"**
```sql
WITH skill_trends AS (
    SELECT 
        d.year,
        d.month,
        j.skills_required,
        COUNT(*) as job_count
    FROM fact_job_postings f
    JOIN dim_job j ON f.job_key = j.job_key
    JOIN dim_date d ON f.date_key = d.date_key
    WHERE j.skills_required IS NOT NULL
    GROUP BY d.year, d.month, j.skills_required
)
SELECT * FROM skill_trends
ORDER BY year, month, job_count DESC;
```

---

## 📊 **DATA FLOW ARCHITECTURE**

### **Current → Target State:**

#### **Current (Bronze Only):**
```
Scrapy → SQL Server (raw) → FastAPI → Web Dashboard
```

#### **Target (Bronze-Silver-Gold):**
```
                    ┌─ Bronze Layer ─┐
Scrapy → Raw Data   │  Raw job data  │
                    │  Minimal proc. │
                    └────────┬───────┘
                             │
                    ┌─ Silver Layer ─┐
                    │  Cleaned data  │ → Business Reports
                    │  Standardized  │ → KPI Dashboards  
                    └────────┬───────┘
                             │
                    ┌─ Gold Layer ───┐
                    │  Analytics     │ → ML Models
                    │  Aggregations  │ → Advanced Analytics
                    │  Business KPIs │ → Executive Dashboards
                    └────────────────┘
```

---

## 🚀 **IMPLEMENTATION ROADMAP**

### **Week 1-2: Foundation**
```
📋 Tasks:
1. Design dimensional model (manual)
2. Create dimension tables (manual)  
3. Build basic ETL scripts (manual)
4. Setup data validation (manual)

🎯 Deliverable: Working dimensional model với sample data
```

### **Week 3-4: Bronze → Silver Pipeline**
```
📋 Tasks:
1. Data cleaning functions (manual logic)
2. Standardization rules (manual definition)
3. Automated execution (cron jobs)
4. Quality monitoring (automated alerts)

🎯 Deliverable: Clean, standardized data ready for analysis
```

### **Week 5-6: Gold Layer & Analytics**
```
📋 Tasks:
1. Business KPIs definition (manual)
2. Aggregation pipelines (automated)
3. Analytics dashboard (manual design)
4. Performance optimization (automated)

🎯 Deliverable: Business intelligence dashboard
```

### **Week 7-8: Advanced Features**
```
📋 Tasks:
1. ML job matching (manual algorithm design)
2. Trend analysis (automated calculations)
3. Recommendation engine (hybrid)
4. API enhancements (manual endpoints)

🎯 Deliverable: Smart job platform với ML features
```

---

## 💡 **PRACTICAL TIPS**

### **Start Small, Scale Smart:**
```
✅ Do:
- Begin với 1-2 business questions
- Focus on data quality first
- Automate gradually  
- Document everything

❌ Don't:
- Build everything at once
- Over-engineer từ đầu
- Ignore data quality
- Skip documentation
```

### **Common Pitfalls & Solutions:**
```
🚨 Pitfall: "Perfect schema from day 1"
✅ Solution: Start simple, evolve schema

🚨 Pitfall: "Automate everything immediately"  
✅ Solution: Manual → Semi-auto → Full auto

🚨 Pitfall: "Complex tools from start"
✅ Solution: Python scripts → Airflow → Enterprise tools
```

---

## 🎯 **SUCCESS METRICS**

### **Technical Metrics:**
- Data quality score > 90%
- ETL success rate > 95%
- Query response time < 5s
- Data freshness < 24h

### **Business Metrics:**
- User engagement với analytics
- Decision making speed improvement
- Cost reduction từ automation
- Time-to-insight reduction

---

## 📚 **LEARNING PATH**

### **Fundamentals (Week 1-2):**
1. Kimball dimensional modeling
2. SQL performance tuning
3. Data quality concepts
4. ETL best practices

### **Implementation (Week 3-6):**
1. Python data processing (Pandas)
2. Database design patterns
3. API development (FastAPI)
4. Testing strategies

### **Advanced (Week 7-10):**
1. Apache Airflow
2. Docker containerization
3. ML for recommendations
4. Production deployment

---

**🎉 Kết luận: Data Warehouse KHÔNG hoàn toàn tự động. Cần kết hợp manual design (business logic, data modeling) với automated execution (ETL, monitoring). Start từ business requirements, design dimensional model, sau đó tự động hóa dần dần.**

**Bạn muốn tôi detail hóa bước nào trước?** 🤔

*(Based on 8 năm experience implement DW cho 15+ companies)*
