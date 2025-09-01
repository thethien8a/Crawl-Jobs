# 🚀 **DEVELOPER GETTING STARTED GUIDE**
## **CrawlJob Data Warehouse Project**

---

## 📋 **TABLE OF CONTENTS**

1. [🎯 Project Overview](#-project-overview)
2. [🏗️ Current System Status](#️-current-system-status)
3. [🛠️ Development Environment Setup](#️-development-environment-setup)
4. [📊 Data Warehouse Implementation](#-data-warehouse-implementation)
5. [🔧 Quick Start Commands](#-quick-start-commands)
6. [📁 Project Structure](#-project-structure)
7. [🎯 What You Need To Do](#-what-you-need-to-do)

---

## 🎯 **PROJECT OVERVIEW**

### **What is CrawlJob?**
CrawlJob là hệ thống web scraping chuyên nghiệp thu thập dữ liệu việc làm từ **10 trang tuyển dụng Việt Nam**:
- JobsGO, JobOKO, 123Job, CareerViet, JobStreet
- LinkedIn, TopCV, ITviec, CareerLink, VietnamWorks

### **Current Status: ✅ PRODUCTION READY**
- ✅ **10 spiders** hoạt động hoàn hảo
- ✅ **SQL Server database** với 10,000+ records
- ✅ **FastAPI backend** với REST endpoints
- ✅ **Web dashboard** với Bootstrap 5
- ✅ **Automated daily crawling**

### **Next Phase: 🏗️ DATA WAREHOUSE**
Chuyển đổi từ **Job Scraping System** → **Business Intelligence Platform**

---

## 🏗️ **CURRENT SYSTEM STATUS**

### **✅ What's Already Built**

#### **1. Scrapy Spiders (10 sites)**
```bash
# Location: CrawlJob/spiders/
├── jobsgo_spider.py      # JobsGO.vn - CSS selectors
├── joboko_spider.py      # JobOKO.com - CSS selectors  
├── job123_spider.py      # 123Job.vn - CSS selectors
├── careerviet_spider.py  # CareerViet.vn - CSS selectors
├── jobstreet_spider.py   # JobStreet.vn - CSS selectors
├── linkedin_spider.py    # LinkedIn.com - Selenium
├── topcv_spider.py       # TopCV.vn - JavaScript parsing
├── itviec_spider.py      # ITviec.com - Undetected ChromeDriver
├── careerlink_spider.py  # CareerLink.vn - Selenium
└── vietnamworks_spider.py # VietnamWorks.com - Selenium
```

#### **2. Database Schema**
```sql
-- Current table: jobs
CREATE TABLE jobs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    job_title NVARCHAR(500),
    company_name NVARCHAR(200),
    salary NVARCHAR(100),
    location NVARCHAR(200),
    job_type NVARCHAR(100),
    experience_level NVARCHAR(100),
    education_level NVARCHAR(100),
    job_industry NVARCHAR(200),
    job_position NVARCHAR(200),
    job_description NVARCHAR(MAX),
    requirements NVARCHAR(MAX),
    benefits NVARCHAR(MAX),
    job_deadline NVARCHAR(100),
    source_site NVARCHAR(100),
    job_url NVARCHAR(1000),
    search_keyword NVARCHAR(200),
    scraped_at NVARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NULL
);
```

#### **3. API Endpoints**
```python
# Location: api/main.py
GET /health                    # Health check
GET /jobs?keyword=X&page=Y     # Job search with pagination
```

#### **4. Web Dashboard**
```bash
# Location: web/
├── index.html          # Main dashboard
├── css/styles.css      # Styling
├── css/responsive.css  # Mobile responsive
├── js/main.js          # Core logic
├── js/api.js           # API communication
└── js/ui.js            # UI helpers
```

---

## 🛠️ **DEVELOPMENT ENVIRONMENT SETUP**

### **Prerequisites**
```bash
# Required software
✅ Python 3.12.2
✅ SQL Server (local or remote)
✅ Docker Desktop
✅ Git
✅ VS Code (recommended)
```

### **Step 1: Clone & Setup**
```bash
# Clone project
git clone <repository-url>
cd D:\Practice\Scrapy\CrawlJob

# Create virtual environment
python -m venv venv
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt
```

### **Step 2: Database Setup**
```bash
# Create .env file
cp env.example .env

# Edit .env with your database credentials
SQL_SERVER=localhost
SQL_DATABASE=JobDatabase
SQL_USERNAME=sa
SQL_PASSWORD=your_password
```

### **Step 3: Test Current System**
```bash
# Test individual spider
python run_spider.py --spider jobsgo --keyword "Python Developer"

# Test API
uvicorn api.main:app --reload
# Access: http://localhost:8000/health

# Test web dashboard
# Open: web/index.html in browser
```

---

## 📊 **DATA WAREHOUSE IMPLEMENTATION**

### **🎯 Your Main Task: Build Data Warehouse**

#### **Architecture Overview**
```
Current: CrawlJob → SQL Server (OLTP)
Target:  CrawlJob → Data Warehouse (OLAP)
         ├── Bronze Layer (Raw Data)
         ├── Silver Layer (Cleaned Data)  
         └── Gold Layer (Analytics)
```

#### **Technology Stack**
- **dbt**: Data transformation và modeling
- **Apache Airflow**: Pipeline orchestration
- **Great Expectations**: Data quality validation
- **Docker**: Containerization
- **SQL Server**: Database (existing)

### **Implementation Phases**

#### **Phase 1: Foundation (Week 1-2)**
- [ ] Deploy Docker environment
- [ ] Build Bronze layer ETL
- [ ] Create monitoring dashboard

#### **Phase 2: Silver Layer (Week 2-4)**
- [ ] Implement data cleaning
- [ ] Add quality validations
- [ ] Build dimensional model

#### **Phase 3: Gold Layer (Week 4-6)**
- [ ] Create business KPIs
- [ ] Build analytics dashboards
- [ ] Implement automation

#### **Phase 4: Production (Week 6-8)**
- [ ] Cloud deployment
- [ ] Monitoring & alerting
- [ ] Go-live preparation

---

## 🔧 **QUICK START COMMANDS**

### **Current System Commands**
```bash
# Run individual spider
python run_spider.py --spider jobsgo --keyword "Data Analyst"

# Run all spiders
python run_spider.py --spider all --keyword "IT Developer"

# Start API server
uvicorn api.main:app --reload

# Check database
sqlcmd -S localhost -U sa -P password -Q "SELECT COUNT(*) FROM jobs"
```

### **Data Warehouse Commands**
```bash
# Deploy Docker environment
cd deployment
docker-compose up -d

# Access Airflow
# http://localhost:8080 (admin/admin)

# Access monitoring dashboard
# http://localhost:8501

# Run dbt
dbt run --project-dir dbt_project
dbt test --project-dir dbt_project
```

---

## 📁 **PROJECT STRUCTURE**

```
D:\Practice\Scrapy\CrawlJob\
├── 📋 plan/                          # 📋 ALL PROJECT PLANS HERE
│   ├── COMPLETE_DATA_WAREHOUSE_GUIDE.md  # 🎯 MASTER PLAN FILE
│   ├── DEVELOPER_GETTING_STARTED.md      # 📖 This file
│   ├── ARCHITECTURE_OVERVIEW.md          # 🏗️ Technical architecture
│   ├── IMPLEMENTATION_ROADMAP.md         # 🚀 Step-by-step guide
│   ├── API_REFERENCE.md                 # 📚 API documentation
│   ├── DEPLOYMENT_GUIDE.md              # ☁️ Production deployment
│   ├── TROUBLESHOOTING.md               # 🔧 Common issues
│   └── DATABASE_SCHEMA.md               # 🗄️ Database design
│
├── 🕷️ CrawlJob/                      # 🕷️ Scrapy spiders (10 sites)
│   ├── spiders/
│   ├── items.py
│   ├── pipelines.py
│   └── settings.py
│
├── 🚀 api/                           # 🚀 FastAPI backend
│   └── main.py
│
├── 🌐 web/                           # 🌐 Frontend dashboard
│   ├── index.html
│   ├── css/
│   └── js/
│
├── 🐳 deployment/                    # 🐳 Docker & deployment
│   ├── docker-compose.yml
│   ├── dags/
│   └── monitoring/
│
├── 📊 dbt_project/                   # 📊 Data transformation
│   ├── models/
│   ├── tests/
│   └── dbt_project.yml
│
├── 📝 logs/                          # 📝 Crawling logs
├── 💾 outputs/                       # 💾 JSON output files
└── 🧪 test/                          # 🧪 Testing framework
```

---

## 🎯 **WHAT YOU NEED TO DO**

### **Immediate Tasks (Today)**

#### **1. Understand Current System**
- [ ] Read `plan/COMPLETE_DATA_WAREHOUSE_GUIDE.md`
- [ ] Test current spiders: `python run_spider.py --spider jobsgo --keyword "test"`
- [ ] Check database: `sqlcmd -S localhost -U sa -P password -Q "SELECT TOP 10 * FROM jobs"`
- [ ] Test API: `curl http://localhost:8000/health`

#### **2. Setup Development Environment**
- [ ] Install Docker Desktop
- [ ] Create `deployment/` directory
- [ ] Copy Docker configuration from guide
- [ ] Test Docker setup

#### **3. Start Data Warehouse Implementation**
- [ ] Deploy Docker environment
- [ ] Create Bronze layer ETL
- [ ] Build basic monitoring dashboard

### **This Week Tasks**

#### **Week 1: Foundation**
- [ ] Complete Docker deployment
- [ ] Implement Bronze layer ETL
- [ ] Create monitoring dashboard
- [ ] Test data flow from CrawlJob → Bronze

#### **Week 2: Silver Layer**
- [ ] Setup dbt project
- [ ] Create staging models
- [ ] Implement data cleaning
- [ ] Build dimensional models

### **Success Criteria**

#### **Technical Success**
- [ ] ETL pipelines run reliably daily
- [ ] Data quality > 90%
- [ ] Query performance < 5 seconds
- [ ] Zero data loss in transformations

#### **Business Success**
- [ ] Business users access insights daily
- [ ] Decision-making speed improved
- [ ] Cost reduction from automation
- [ ] Better job market understanding

---

## 🚀 **NEXT STEPS**

### **Start Here**
1. **Read the master plan**: `plan/COMPLETE_DATA_WAREHOUSE_GUIDE.md`
2. **Setup environment**: Follow this guide
3. **Deploy Docker**: Quick deployment section
4. **Implement Bronze layer**: ETL implementation

### **Key Documents to Read**
- 📖 `plan/ARCHITECTURE_OVERVIEW.md` - Technical architecture
- 📖 `plan/IMPLEMENTATION_ROADMAP.md` - Step-by-step implementation
- 📖 `plan/DEPLOYMENT_GUIDE.md` - Production deployment
- 📖 `plan/TROUBLESHOOTING.md` - Common issues and solutions

### **Support Resources**
- 📚 dbt documentation: https://docs.getdbt.com/
- 📚 Airflow documentation: https://airflow.apache.org/docs/
- 📚 Docker documentation: https://docs.docker.com/

---

## 🎉 **CONCLUSION**

**You're ready to build a professional Data Warehouse!**

**Current Status**: ✅ Production-ready job scraping system
**Next Goal**: 🏗️ Transform into Business Intelligence platform
**Timeline**: 8 weeks to complete implementation
**Technology**: Modern data stack (dbt, Airflow, Docker)

**Start with**: Quick deployment (1 hour) to get MVP running!

---

**Questions?** Check the troubleshooting guide or ask for help. Let's build something amazing! 🔥
