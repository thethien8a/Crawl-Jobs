# 🚀 **DATA ENGINEERING STACK IMPLEMENTATION PLAN**
## **CrawlJob: Professional Data Engineering Project**

---

## 📋 **TABLE OF CONTENTS**

1. [🎯 Project Overview](#-project-overview)
2. [🏗️ Architecture Design](#️-architecture-design)
3. [📊 Implementation Phases](#-implementation-phases)
4. [🔧 Technical Implementation](#-technical-implementation)
5. [📈 Success Metrics](#-success-metrics)
6. [🚀 Deployment Guide](#-deployment-guide)

---

## 🎯 **PROJECT OVERVIEW**

### **Current Status**
- ✅ **10 Spiders** hoạt động hoàn hảo
- ✅ **PostgreSQL** database với 10,000+ records
- ✅ **FastAPI** backend với REST endpoints
- ✅ **Web Dashboard** với Bootstrap 5
- ✅ **Automated daily crawling**

### **Data Engineering Goal**
Chuyển đổi CrawlJob thành **Professional Data Engineering Project** với:
- **Apache Airflow**: Workflow orchestration
- **dbt**: Data transformation layer
- **Great Expectations**: Data quality validation
- **Power BI**: Data visualization và analytics

### **Benefits**
- 🏢 **Professional**: Industry-standard data engineering stack
- 📊 **Advanced Analytics**: Rich dashboards và insights
- 🔧 **Automation**: Fully automated pipelines
- 📈 **Scalability**: Easy to scale as project grows
- 💼 **Career Growth**: Valuable skills for data engineering

---

## 🏗️ **ARCHITECTURE DESIGN**

### **Current Architecture**
```
CrawlJob Spiders → PostgreSQL → FastAPI → Web Dashboard
```

### **Target Data Engineering Architecture**
```
CrawlJob Spiders → Apache Airflow → PostgreSQL (OLTP) → dbt → DuckDB (OLAP)
                                    ↓
                              Great Expectations → Data Quality Reports
                                    ↓
                              Power BI → Analytics Dashboards
```

### **Technology Stack**
- **Orchestration**: Apache Airflow
- **OLTP Database**: PostgreSQL
- **OLAP Database**: DuckDB
- **Transformation**: dbt
- **Data Quality**: Great Expectations
- **Visualization**: Power BI
- **Backend**: FastAPI
- **Frontend**: Bootstrap 5

---

## 📊 **IMPLEMENTATION PHASES**

### **Phase 1: Core Data Engineering (Tuần 1-4)**

#### **Week 1-2: Apache Airflow Setup**
- ✅ Install Apache Airflow
- ✅ Create DAGs cho spider scheduling
- ✅ Setup database connections
- ✅ Configure error handling và retries
- ✅ Test với existing spiders
- ✅ Setup monitoring và alerts

#### **Week 3-4: dbt Integration**
- ✅ Install dbt-core + dbt-postgres
- ✅ Create dbt project structure
- ✅ Build transformation models
- ✅ Setup dbt docs
- ✅ Test data transformations
- ✅ Create data lineage

### **Phase 2: Data Quality & Visualization (Tuần 5-8)**

#### **Week 5-6: Great Expectations**
- ✅ Install Great Expectations
- ✅ Create data quality checks
- ✅ Setup validation pipelines
- ✅ Integrate với Airflow
- ✅ Generate quality reports
- ✅ Setup quality monitoring

#### **Week 7-8: Power BI Integration**
- ✅ Setup Power BI Desktop
- ✅ Connect to PostgreSQL/DuckDB
- ✅ Create job market dashboards
- ✅ Setup data refresh schedules
- ✅ Deploy Power BI Service
- ✅ Setup user access controls

---

## 🔧 **TECHNICAL IMPLEMENTATION**

### **1. Apache Airflow Configuration**

#### **DAG Structure**
```python
# crawljob_dag.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'crawljob',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'crawljob_daily_pipeline',
    default_args=default_args,
    description='Daily job crawling pipeline',
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    catchup=False,
    tags=['crawljob', 'daily', 'jobs']
)

# Spider execution tasks
spider_tasks = []
for spider in ['careerlink', 'careerviet', 'itviec', 'job123', 'joboko', 'jobsgo', 'jobstreet', 'linkedin', 'topcv', 'vietnamworks']:
    task = BashOperator(
        task_id=f'run_{spider}_spider',
        bash_command=f'cd /path/to/crawljob && scrapy crawl {spider}',
        dag=dag
    )
    spider_tasks.append(task)

# Data quality check
quality_check = PythonOperator(
    task_id='data_quality_check',
    python_callable=run_data_quality_checks,
    dag=dag
)

# dbt transformation
dbt_run = BashOperator(
    task_id='dbt_transformation',
    bash_command='cd /path/to/dbt/project && dbt run',
    dag=dag
)

# Set dependencies
spider_tasks >> quality_check >> dbt_run
```

#### **Connection Configuration**
```python
# airflow/connections.py
from airflow.models import Connection

# PostgreSQL connection
postgres_conn = Connection(
    conn_id='postgresql_default',
    conn_type='postgres',
    host='localhost',
    port=5432,
    login='crawljob_user',
    password='your_password',
    schema='crawljob_db'
)

# DuckDB connection
duckdb_conn = Connection(
    conn_id='duckdb_default',
    conn_type='duckdb',
    host='localhost',
    port=5432,
    login='analytics_user',
    password='your_password',
    schema='analytics_db'
)
```

### **2. dbt Configuration**

#### **dbt_project.yml**
```yaml
name: 'crawljob_analytics'
version: '1.0.0'
config-version: 2

profile: 'crawljob'

model-paths: ["models"]
analysis-paths: ["analysis"]
test-paths: ["tests"]
seed-paths: ["seeds"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

target-path: "target"
clean-targets:
  - "target"
  - "dbt_packages"

models:
  crawljob_analytics:
    staging:
      +materialized: view
    marts:
      +materialized: table
```

#### **profiles.yml**
```yaml
crawljob:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      user: crawljob_user
      password: your_password
      port: 5432
      dbname: crawljob_db
      schema: analytics
      threads: 4
      keepalives_idle: 0
```

#### **Sample Model: stg_jobs.sql**
```sql
-- models/staging/stg_jobs.sql
with source as (
    select * from {{ source('raw', 'jobs') }}
),

renamed as (
    select
        id,
        job_title,
        company_name,
        salary,
        location,
        job_type,
        job_industry,
        experience_level,
        education_level,
        job_position,
        job_description,
        job_requirements,
        job_benefits,
        job_url,
        company_url,
        company_size,
        company_industry,
        posted_date,
        created_at,
        updated_at
    from source
)

select * from renamed
```

#### **Sample Model: dim_companies.sql**
```sql
-- models/marts/dim_companies.sql
with companies as (
    select distinct
        company_name,
        company_url,
        company_size,
        company_industry
    from {{ ref('stg_jobs') }}
),

company_stats as (
    select
        company_name,
        count(*) as total_jobs,
        count(distinct job_industry) as industries_count,
        count(distinct location) as locations_count
    from {{ ref('stg_jobs') }}
    group by company_name
)

select
    row_number() over (order by company_name) as company_id,
    c.company_name,
    c.company_url,
    c.company_size,
    c.company_industry,
    cs.total_jobs,
    cs.industries_count,
    cs.locations_count
from companies c
left join company_stats cs on c.company_name = cs.company_name
```

### **3. Great Expectations Configuration**

#### **Data Quality Checks**
```python
# great_expectations/expectations/job_data_quality.py
import great_expectations as gx
from great_expectations.core import ExpectationConfiguration

def create_job_data_quality_suite():
    context = gx.get_context()
    
    # Create expectation suite
    suite = context.create_expectation_suite(
        expectation_suite_name="job_data_quality",
        overwrite_existing=True
    )
    
    # Add expectations
    expectations = [
        # Data completeness
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_not_be_null",
            kwargs={"column": "job_title"}
        ),
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_not_be_null",
            kwargs={"column": "company_name"}
        ),
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_not_be_null",
            kwargs={"column": "job_url"}
        ),
        
        # Data uniqueness
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_unique",
            kwargs={"column": "job_url"}
        ),
        
        # Data freshness
        ExpectationConfiguration(
            expectation_type="expect_column_max_to_be_between",
            kwargs={
                "column": "posted_date",
                "min_value": "2024-01-01",
                "max_value": "now"
            }
        ),
        
        # Data volume
        ExpectationConfiguration(
            expectation_type="expect_table_row_count_to_be_between",
            kwargs={
                "min_value": 1000,
                "max_value": 50000
            }
        )
    ]
    
    for expectation in expectations:
        suite.add_expectation(expectation)
    
    context.save_expectation_suite(suite)
    return suite
```

### **4. Power BI Integration**

#### **Data Source Configuration**
```python
# powerbi/data_connection.py
import pyodbc
import pandas as pd

class PowerBIDataConnector:
    def __init__(self, connection_string):
        self.connection_string = connection_string
    
    def get_job_data(self):
        """Get job data for Power BI"""
        query = """
        SELECT 
            j.job_title,
            j.company_name,
            j.salary,
            j.location,
            j.job_type,
            j.job_industry,
            j.experience_level,
            j.education_level,
            j.posted_date,
            j.created_at,
            c.company_size,
            c.company_industry,
            c.total_jobs
        FROM jobs j
        LEFT JOIN dim_companies c ON j.company_name = c.company_name
        WHERE j.posted_date >= DATEADD(day, -30, GETDATE())
        """
        
        with pyodbc.connect(self.connection_string) as conn:
            return pd.read_sql(query, conn)
    
    def get_analytics_data(self):
        """Get analytics data for Power BI"""
        query = """
        SELECT 
            job_industry,
            location,
            experience_level,
            education_level,
            COUNT(*) as job_count,
            AVG(CASE WHEN salary IS NOT NULL THEN salary END) as avg_salary
        FROM jobs
        WHERE posted_date >= DATEADD(day, -30, GETDATE())
        GROUP BY job_industry, location, experience_level, education_level
        """
        
        with pyodbc.connect(self.connection_string) as conn:
            return pd.read_sql(query, conn)
```

#### **Power BI Dashboard Structure**
```
📊 CrawlJob Analytics Dashboard
├── 📈 Job Market Overview
│   ├── Total Jobs by Industry
│   ├── Jobs by Location
│   ├── Salary Distribution
│   └── Job Trends Over Time
├── 🏢 Company Analysis
│   ├── Top Companies by Job Count
│   ├── Company Size Distribution
│   ├── Company Industry Breakdown
│   └── Company Growth Trends
├── 💼 Job Requirements
│   ├── Experience Level Distribution
│   ├── Education Requirements
│   ├── Job Type Breakdown
│   └── Skills Demand Analysis
└── 📊 Data Quality
    ├── Data Completeness Score
    ├── Data Freshness Status
    ├── Quality Trends
    └── Data Volume Metrics
```

---

## 📈 **SUCCESS METRICS**

### **Technical Metrics**
- ✅ **Pipeline Uptime**: > 99%
- ✅ **Data Freshness**: < 24 hours
- ✅ **Data Quality Score**: > 95%
- ✅ **Processing Time**: < 2 hours for daily pipeline
- ✅ **Error Rate**: < 1%

### **Business Metrics**
- ✅ **Dashboard Usage**: > 80% daily active users
- ✅ **Data Accuracy**: > 98%
- ✅ **User Satisfaction**: > 4.5/5
- ✅ **Insight Generation**: > 10 new insights per week
- ✅ **Decision Support**: > 90% of decisions data-driven

### **Operational Metrics**
- ✅ **Automation Level**: 100% automated pipelines
- ✅ **Monitoring Coverage**: 100% of critical processes
- ✅ **Alert Response Time**: < 15 minutes
- ✅ **Documentation Coverage**: > 95%
- ✅ **Team Productivity**: > 50% improvement

---

## 🚀 **DEPLOYMENT GUIDE**

### **Environment Setup**

#### **1. Apache Airflow**
```bash
# Install Airflow
pip install apache-airflow

# Initialize database
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@crawljob.com

# Start Airflow
airflow webserver --port 8080
airflow scheduler
```

#### **2. dbt**
```bash
# Install dbt
pip install dbt-core dbt-postgres

# Initialize project
dbt init crawljob_analytics

# Test connection
dbt debug

# Run models
dbt run
```

#### **3. Great Expectations**
```bash
# Install Great Expectations
pip install great_expectations

# Initialize project
great_expectations init

# Create datasource
great_expectations datasource new

# Create expectation suite
great_expectations suite new
```

#### **4. Power BI**
```bash
# Install Power BI Desktop
# Download from Microsoft Store or website

# Install Python connector
pip install pyodbc pandas

# Setup data gateway
# Configure on-premises data gateway
```

### **Production Deployment**

#### **Docker Compose**
```yaml
# docker-compose.yml
version: '3.8'

services:
  postgresql:
    image: postgres:15
    environment:
      POSTGRES_DB: crawljob_db
      POSTGRES_USER: crawljob_user
      POSTGRES_PASSWORD: your_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  airflow:
    image: apache/airflow:2.8.1
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://crawljob_user:your_password@postgresql:5432/crawljob_db
    ports:
      - "8080:8080"
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
    depends_on:
      - postgresql

  dbt:
    image: dbt/dbt:latest
    volumes:
      - ./dbt:/dbt
    working_dir: /dbt
    command: dbt run

volumes:
  postgres_data:
```

### **Monitoring & Alerting**

#### **Airflow Monitoring**
```python
# airflow/monitoring.py
from airflow.models import DagRun
from airflow.utils.state import State
from airflow.utils.dates import days_ago

def check_dag_status():
    """Check DAG run status and send alerts"""
    dag_runs = DagRun.find(
        dag_id='crawljob_daily_pipeline',
        state=State.FAILED,
        execution_date_gte=days_ago(1)
    )
    
    if dag_runs:
        send_alert(f"Failed DAG runs: {len(dag_runs)}")
```

#### **Data Quality Monitoring**
```python
# monitoring/data_quality.py
import great_expectations as gx

def monitor_data_quality():
    """Monitor data quality and send alerts"""
    context = gx.get_context()
    
    # Run checkpoint
    checkpoint_result = context.run_checkpoint(
        checkpoint_name="job_data_quality_checkpoint"
    )
    
    if not checkpoint_result.success:
        send_alert("Data quality check failed")
```

---

## 📚 **RESOURCES & DOCUMENTATION**

### **Documentation**
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [dbt Documentation](https://docs.getdbt.com/)
- [Great Expectations Documentation](https://docs.greatexpectations.io/)
- [Power BI Documentation](https://docs.microsoft.com/en-us/power-bi/)

### **Learning Resources**
- [Data Engineering with Apache Airflow](https://www.oreilly.com/library/view/data-pipelines-with/9781492087823/)
- [dbt Fundamentals](https://courses.getdbt.com/)
- [Great Expectations Tutorial](https://docs.greatexpectations.io/docs/tutorials/)
- [Power BI Training](https://docs.microsoft.com/en-us/learn/powerplatform/power-bi/)

### **Community**
- [Apache Airflow Slack](https://apache-airflow.slack.com/)
- [dbt Community](https://getdbt.com/community/)
- [Great Expectations Discord](https://discord.gg/great-expectations)
- [Power BI Community](https://community.powerbi.com/)

---

## 🎯 **CONCLUSION**

Việc tích hợp **Apache Airflow + dbt + Great Expectations + Power BI** sẽ biến CrawlJob thành một **professional data engineering project** với:

- ✅ **Industry-standard tools**
- ✅ **Automated pipelines**
- ✅ **Data quality assurance**
- ✅ **Rich analytics dashboards**
- ✅ **Scalable architecture**
- ✅ **Professional documentation**

Đây sẽ là một **impressive portfolio project** cho data engineering career và sẵn sàng cho production environment.

---

**Next Steps**: Bắt đầu với **Apache Airflow** setup và tạo DAGs cho spider scheduling!
