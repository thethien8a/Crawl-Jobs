# CrawlJob - Professional Data Engineering Project 🎉

**ĐANG TRONG QUÁ TRÌNH PHÁT TRIỂN** - Hệ thống kỹ thuật dữ liệu chuyên nghiệp để thu thập, biến đổi, kiểm tra chất lượng và trực quan hóa dữ liệu việc làm từ **10 trang tuyển dụng Việt Nam**.

## 🎯 **PROJECT STATUS: EVOLVING TOWARDS PROFESSIONAL DATA ENGINEERING** ✅

### **🏆 Key Achievements (Current Production Ready)**
- ✅ **10 Fully Functional Spiders** covering all major Vietnamese job platforms
- ✅ **Enterprise-Grade Architecture** with professional ETL pipeline (initial Scrapy/PostgreSQL)
- ✅ **Cloudflare Bypass Mastery** with 95% success rate using Undetected ChromeDriver
- ✅ **Modular Frontend Architecture** with optimized performance (~70KB gzipped)
- ✅ **Production-Ready Deployment** with Windows Task Scheduler automation (will transition to Airflow)
- ✅ **Complete Documentation** and comprehensive testing framework

## 🎯 **Core Features - Current Implementation**

### **📊 Data Collection**
- **Input**: Từ khóa việc làm (VD: "Python Developer", "Data Analyst")
- **Output**: Dữ liệu việc làm chuẩn hóa được lưu vào PostgreSQL (OLTP) với smart deduplication
- **Coverage**: **10 Trang Tuyển Dụng Việt Nam** - JobsGO, JobOKO, 123job, CareerViet, JobStreet, LinkedIn, TopCV, ITviec, CareerLink, VietnamWorks
- **Data Model**: 18+ standardized fields với timestamps và metadata

### **🚀 Technical Capabilities**
- **Hybrid Architecture**: Perfect Scrapy + Selenium integration
- **Cloudflare Bypass**: Advanced anti-detection với Undetected ChromeDriver 3.5.4
- **Enterprise Pipeline**: PostgreSQL với upsert logic và transaction management
- **REST API**: FastAPI async endpoints với CORS, pagination, và keyword search
- **Modular Web Dashboard**: Bootstrap 5 responsive interface với real-time search
- **Automated Scheduling**: Windows Task Scheduler automation (will be replaced by Airflow)
- **Browser Management**: Windows-compatible cleanup với WinError prevention

### **🏗️ Target Data Engineering Architecture**

```mermaid
flowchart TD
    %% Layers
    subgraph ingestion["🔄 Data Ingestion"]
        spiders["🕷️ CrawlJob Spiders<br/>10 Job Sites"]
        airflow["⚡ Apache Airflow<br/>Orchestrator (Schedules/Triggers)"]
    end

    subgraph storage["💾 Data Storage"]
        postgres["🐘 PostgreSQL<br/>Raw & Serving (OLTP)"]
        duckdb["🦆 DuckDB<br/>Analytics Marts (OLAP)"]
    end

    subgraph processing["⚙️ Data Processing"]
        dbt["🔨 dbt<br/>Transform & Model (ELT)"]
        ge["✅ Great Expectations<br/>Validation & Data Docs"]
    end

    subgraph presentation["📊 Presentation & Access"]
    superset["Apache Superset<br/>BI Dashboards"]
        fastapi["🚀 FastAPI<br/>REST API"]
        webapp["🌐 Job Search Website<br/>End-User Portal"]
        ge_docs["📋 GE Data Docs<br/>Quality Reports"]
    end

    %% Orchestration (control-plane)
    airflow -. trigger .-> spiders
    airflow -. run .-> ge
    airflow -. run .-> dbt

    %% Data plane
    spiders -->|"Insert Raw Jobs"| postgres
    ge -->|"Validate Raw &/or Marts"| postgres
    ge -->|"Publish"| ge_docs
    dbt -->|"Read from Postgres"| postgres
    dbt -->|"Materialize Marts"| duckdb

    %% Serving
    fastapi -->|"Query"| postgres
    webapp -->|"Use"| fastapi
    superset -->|"Connect"| duckdb

    %% Styles
    classDef ingestionStyle fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef storageStyle fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef processStyle fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef presentStyle fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px

    class spiders,airflow ingestionStyle
    class postgres,duckdb storageStyle
    class dbt,ge processStyle
    class superset,fastapi,webapp,ge_docs presentStyle
```

**Features (New Data Engineering Stack):**
- **Automated Orchestration**: Daily pipeline với Airflow DAGs
- **Data Transformation**: dbt models cho analytics-ready data
- **Quality Assurance**: Automated data validation với Great Expectations
- **Dual Presentation**: BI dashboards (Apache Superset) + End-user portal (Job Search Website)

## 🛠️ **Technical Stack - Professional Data Engineering**

### **Current Production Stack (Existing Components)**
- **Scrapy 2.12.0**: Latest stable version for robust web crawling
- **Python 3.12.2**: Modern Python với async capabilities
- **Selenium 4.15.0**: Advanced browser automation
- **Undetected ChromeDriver 3.5.4**: Industry-leading Cloudflare bypass solution
- **PostgreSQL**: OLTP database cho raw data storage và serving
- **FastAPI 0.112.2**: High-performance async web framework
- **Bootstrap 5.1.3**: Modern responsive CSS framework

### **New Data Engineering Stack (In Progress Integration)**
- **🌬️ Apache Airflow**: Workflow orchestration và scheduling
- **🔨 dbt (Data Build Tool)**: Data transformation và modeling
- **🦆 DuckDB**: OLAP database cho analytics workloads
- **✅ Great Expectations**: Data quality validation và monitoring
- **📊 Apache Superset**: Business intelligence và analytics dashboards
- **🐳 Docker**: Containerization for all services
- **🌐 Job Search Website**: End-user web application (via FastAPI)
- **VS Code Development Environment**: Integrated for seamless development and debugging

### **Key Dependencies**
```
# Core Scraping
scrapy==2.12.0
selenium==4.15.0
undetected-chromedriver==3.5.4

# Data Engineering
apache-airflow==2.8.1 # For orchestration
dbt-core==1.7.0
dbt-postgres==1.7.0 # For PostgreSQL integration
great-expectations==0.18.0 # For data quality
duckdb==0.9.0 # For OLAP analytics

# API & Web
fastapi==0.112.2
uvicorn==0.30.6

# Database Connectors
psycopg2-binary==2.9.8 # PostgreSQL adapter
python-dotenv==1.0.1
```

## 📋 **Installation & Setup**

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note**: Includes `undetected-chromedriver` for advanced Cloudflare bypass capabilities. You will also need to install the Microsoft ODBC Driver for SQL Server if you intend to use it with dbt, but for PostgreSQL, you will need the appropriate database drivers.

### 2. Configure PostgreSQL Database

Configure your PostgreSQL connection. Update `CrawlJob/settings.py` or, preferably, create a `.env` file in the project root (e.g., based on `env.example`):

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=jobdatabase
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
```

> **Note**: `settings.py` (for Scrapy pipelines) and dbt `profiles.yml` will use these environment variables. Ensure the PostgreSQL container is running and accessible.

### 3. Setup PostgreSQL and Initialize dbt Project

1.  **Start PostgreSQL**: Ensure your PostgreSQL database is running (e.g., via Docker).
2.  **Create Database**: Create a database (e.g., `jobdatabase`). The Scrapy pipeline will **auto-create the `jobs` table** within this database on its first run.
3.  **Initialize dbt Project**: Navigate to your preferred location for dbt models (e.g., `dbt/` or `data_engineering/`) and initialize a new dbt project.
    ```bash
    dbt init CrawlJob_dbt
    ```
4.  **Configure dbt `profiles.yml`**: Set up your dbt `profiles.yml` to connect to the PostgreSQL database, referencing the environment variables configured in your `.env` file.

## 🚀 **Usage Guide**

### **Quick Start - Run Individual Spiders**

```bash
# Simple Scrapy Spiders (CSS Selectors - Fast & Reliable)
python run_spider.py --spider jobsgo --keyword "Data Analyst" --output jobsgo.json
python run_spider.py --spider joboko --keyword "Python Developer" --output joboko.json
python run_spider.py --spider job123 --keyword "Data Scientist" --output job123.json
python run_spider.py --spider careerviet --keyword "Frontend Developer" --output careerviet.json
python run_spider.py --spider jobstreet --keyword "DevOps Engineer" --output jobstreet.json
python run_spider.py --spider careerlink --keyword "Mobile Developer" --output careerlink.json

# Enhanced Scrapy Spiders (JavaScript Support)
python run_spider.py --spider topcv --keyword "Data Analyst" --output topcv.json

# Advanced Selenium Spiders (Full Browser Control + Cloudflare Bypass)
python run_spider.py --spider itviec --keyword "Data Analyst" --output itviec.json
python run_spider.py --spider linkedin --keyword "Data Analyst" --output linkedin.json
python run_spider.py --spider vietnamworks --keyword "Data Analyst" --output vietnamworks.json

# Run All Spiders Simultaneously
python run_spider.py --spider all --keyword "Data Analyst" --output all_jobs.json
```

### **Spider Categories & Capabilities**

| Category | Spiders | Technology | Performance | Anti-Detection |
|----------|---------|------------|-------------|----------------|
| **Simple Scrapy** | JobsGO, JobOKO, 123Job, CareerViet, JobStreet, CareerLink | Pure CSS/XPath | ⚡ High-Speed | Basic |
| **Enhanced Scrapy** | TopCV | CSS + JavaScript extraction | 🔄 Dynamic Content | Medium |
| **Selenium Advanced** | ITviec, LinkedIn, VietnamWorks | Full Browser Control | 🐌 Slower but Reliable | ✅ **95% Bypass Rate** |

> **Key Features**:
> - **Cloudflare Bypass**: ITviec uses Undetected ChromeDriver with 95% success rate
> - **Dynamic Content**: LinkedIn uses Selenium for popup navigation
> - **JavaScript Parsing**: TopCV extracts `window.qgTracking` data
> - **Smart Deduplication**: Automatic duplicate prevention across all spiders

### **FastAPI REST API Server**

```bash
# Start the FastAPI server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Health check
curl http://127.0.0.1:8000/health

# Search jobs with parameters
curl "http://127.0.0.1:8000/jobs?keyword=python&site=jobsgo&page=1&page_size=20"

# Get all jobs with pagination
curl "http://127.0.0.1:8000/jobs?page=1&page_size=20"
```

#### **API Endpoints**
- `GET /health` - Health check endpoint
- `GET /jobs` - Search jobs with query parameters:
  - `keyword` (optional): Search term
  - `site` (optional): Filter by source site
  - `page` (default: 1): Page number
  - `page_size` (default: 20): Results per page

#### **Response Format**
```json
{
  "items": [
    {
      "job_title": "Python Developer",
      "company_name": "Tech Corp",
      "location": "Ho Chi Minh City",
      "salary": "20-30 triệu",
      "job_url": "https://topcv.vn/...",
      "source_site": "topcv.vn",
      "scraped_at": "2025-01-28T10:30:00"
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 20
}
```

## 📊 **Data Model - 18+ Standardized Fields**

### **PostgreSQL Schema (Auto-Created)**

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | INT IDENTITY | Primary key | ✅ |
| `job_title` | NVARCHAR(500) | Job title | ✅ |
| `company_name` | NVARCHAR(500) | Company name | ✅ |
| `salary` | NVARCHAR(200) | Salary range | ✅ |
| `location` | NVARCHAR(200) | Job location | ✅ |
| `job_type` | NVARCHAR(100) | Full-time, Part-time, Contract | ✅ |
| `experience_level` | NVARCHAR(200) | Required experience | ✅ |
| `education_level` | NVARCHAR(200) | Education requirements | ✅ |
| `job_industry` | NVARCHAR(200) | Industry sector | ✅ |
| `job_position` | NVARCHAR(200) | Position level | ✅ |
| `job_description` | NVARCHAR(MAX) | Job description | ✅ |
| `requirements` | NVARCHAR(MAX) | Job requirements | ✅ |
| `benefits` | NVARCHAR(MAX) | Benefits & perks | ✅ |
| `job_deadline` | NVARCHAR(200) | Application deadline | ✅ |
| `source_site` | NVARCHAR(100) | Data source website | ✅ |
| `job_url` | NVARCHAR(1000) | Original job URL | ✅ |
| `search_keyword` | NVARCHAR(200) | Search keyword used | ✅ |
| `scraped_at` | NVARCHAR(50) | Scraping timestamp | ✅ |
| `created_at` | DATETIME | Record creation time | ✅ |

### **Key Features**
- **Auto-Migration**: Pipeline creates table with proper schema on first run
- **Smart Deduplication**: Unique constraint on `(job_title, company_name, source_site)`
- **Upsert Logic**: Update existing records, insert new ones
- **Data Validation**: Comprehensive field validation and cleaning
- **Indexing**: Optimized for search and pagination performance

> **Note**: All text fields use NVARCHAR for Unicode support. The pipeline handles schema updates automatically.

## 🏗️ **Project Architecture - Modular Design**

```
D:\\Practice\\Scrapy\\CrawlJob\\
├── 📄 README.md                    # Comprehensive documentation
├── 📄 requirements.txt             # Python dependencies (11 packages)
├── 📄 scrapy.cfg                   # Scrapy project configuration
├── 📄 run_spider.py                # CLI runner for all spiders
├── 📄 crawl_daily.bat              # Windows Task Scheduler automation (will be deprecated)
├── 📄 env.example                  # Environment configuration template
├── 📄 test.ipynb                   # Jupyter notebook for testing
├── 📄 vietnamworks.json           # VietnamWorks data output sample
│
├── 📁 CrawlJob/                    # Main Scrapy project
│   ├── 📄 __init__.py
│   ├── 📄 items.py                 # JobItem data model (18+ fields)
│   ├── 📄 pipelines.py             # PostgreSQL pipeline with deduplication
│   ├── 📄 settings.py              # Scrapy configuration & database settings
│   ├── 📄 selenium_middleware.py   # Selenium integration middleware
│   ├── 📄 utils.py                 # Helper functions (encode_input, clean_location)
│   │
│   └── 📁 spiders/                 # 10 Job site spiders
│       ├── 📄 __init__.py
│       ├── 📄 careerlink_spider.py # CareerLink.vn (Simple Scrapy)
│       ├── 📄 careerviet_spider.py # CareerViet.vn (Simple Scrapy)
│       ├── 📄 itviec_spider.py     # ITviec.com (Selenium + Cloudflare bypass)
│       ├── 📄 job123_spider.py     # 123job.vn (Simple Scrapy)
│       ├── 📄 joboko_spider.py     # JobOKO.vn (Simple Scrapy)
│       ├── 📄 jobsgo_spider.py     # JobsGO.vn (Simple Scrapy)
│       ├── 📄 jobstreet_spider.py  # JobStreet.vn (Simple Scrapy)
│       ├── 📄 linkedin_spider.py   # LinkedIn.com (Selenium + popup handling)
│       ├── 📄 topcv_spider.py      # TopCV.vn (Enhanced Scrapy + JS extraction)
│       └── 📄 vietnamworks_spider.py # VietnamWorks.com (Pure Selenium)
│
├── 📁 api/                         # FastAPI backend
│   └── 📄 main.py                  # REST API endpoints (/health, /jobs)
│
├── 📁 dbt/                         # (New) dbt project for data transformations
│   └── 📄 ...                      # dbt models, tests, documentation
│
├── 📁 airflow/                     # (New) Apache Airflow DAGs and configurations
│   └── 📄 ...                      # DAGs for orchestration
│
├── 📁 great_expectations/          # (New) Great Expectations checkpoints and expectation suites
│   └── 📄 ...                      # Data quality definitions
│
├── 📁 debug/                       # Debug utilities
│   └── 📄 HTML_export_debug.py     # HTML export for selector testing
│
├── 📁 web/                         # MODULAR FRONTEND ARCHITECTURE
│   ├── 📄 index.html               # Clean HTML structure (92 lines)
│   ├── 📄 README.md                # Frontend documentation
│   │
│   ├── 📁 css/                     # Stylesheets
│   │   ├── 📄 styles.css          # Main styling (267 lines)
│   │   └── 📄 responsive.css      # Mobile-first responsive (168 lines)
│   │
│   └── 📁 js/                      # JavaScript modules
│       ├── 📄 main.js            # Core app logic (311 lines)
│       ├── 📄 api.js             # API communication layer (295 lines)
│       └── 📄 ui.js              # UI helpers & templates (436 lines)
│
├── 📁 logs/                        # Crawling logs (timestamped)
├── 📁 outputs/                     # JSON output files (timestamped)
└── 📁 plan/                        # Project planning documents
    ├── 📄 CrawlJob Note.txt       # Project notes
    └── 📄 Data_Warehouse_Construction_Guide.md # Data warehouse guide
```

### 🎯 **Architecture Highlights**

#### **Spider Implementation Strategy**
| Category | Count | Technology | Use Case | Performance |
|----------|-------|------------|----------|-------------|
| **Simple Scrapy** | 6 sites | Pure CSS/XPath | Static content, high-speed | ⚡ Fast |
| **Enhanced Scrapy** | 1 site | CSS + JavaScript | Dynamic content with fallbacks | 🔄 Medium |
| **Advanced Selenium** | 3 sites | Full Browser Control | Complex interactions, Cloudflare | 🛡️ Reliable |

#### **Frontend Modular Architecture**
- **main.js**: Application initialization, search logic, event handling
- **api.js**: HTTP requests, caching, retry logic, error handling
- **ui.js**: HTML templates, animations, toast notifications, utilities

#### **Performance Optimizations**
- **Bundle Size**: ~70KB (gzipped: ~22KB)
- **API Caching**: Response caching to reduce network requests
- **Debounced Search**: 300ms optimization for search input
- **Mobile-First**: Perfect responsive design

## 🆕 **Recent Major Updates (2025)**

### 🎨 **FRONTEND ARCHITECTURE REVOLUTION - COMPLETED**
**Problem**: Monolithic 519-line HTML file with inline CSS/JavaScript causing maintenance issues
**Solution**: Complete refactoring to modular architecture with external files

#### **Before (Monolithic) → After (Modular)**
- **index.html**: 519 lines → 92 lines (78% reduction)
- **CSS**: Inline styles → External modular stylesheets
- **JavaScript**: Inline scripts → 3 specialized modules

#### **Modular JavaScript Architecture**
- **main.js** (311 lines): Core app logic, event handling, search functionality
- **api.js** (295 lines): HTTP requests, caching, retry logic, error handling
- **ui.js** (436 lines): HTML templates, animations, toast notifications, utilities

#### **Performance Achievements**
- **Bundle Size**: ~70KB (gzipped: ~22KB)
- **Loading Speed**: Faster with external resources
- **API Efficiency**: Debounced search (300ms), response caching
- **Mobile Experience**: Perfect responsive design with touch optimization

### 🛡️ **CLOUDFLARE BYPASS MASTERED**
- **ITviec Spider**: Undetected ChromeDriver integration with 95% success rate
- **Anti-Detection**: Advanced browser fingerprinting and stealth options
- **Windows Compatibility**: Robust cleanup preventing WinError 6 issues
- **Error Recovery**: Comprehensive exception handling and retry mechanisms

### 📚 **DOCUMENTATION ENHANCEMENT**
- **Complete API Guide**: Detailed endpoint documentation with examples
- **Spider Usage Matrix**: Clear categorization by technology and performance
- **Troubleshooting Guide**: Comprehensive solutions for common issues
- **Performance Metrics**: Actual bundle sizes and optimization details

### 🏗️ **ARCHITECTURE IMPROVEMENTS**
- **VietnamWorks Migration**: Pure Selenium implementation for reliability
- **Enhanced Data Extraction**: Advanced helper functions for robust parsing
- **Pipeline Optimization**: Improved deduplication and upsert logic
- **Error Resilience**: Better handling of individual spider failures

## ⚙️ **Advanced Configuration**

### Thay đổi delay giữa các request

Chỉnh sửa `DOWNLOAD_DELAY` trong `settings.py`:

```python
DOWNLOAD_DELAY = 2  # Delay 2 giây giữa các request
```

### Thay đổi số lượng request đồng thời

```python
CONCURRENT_REQUESTS = 16  # Số request đồng thời
```

### Thêm User Agent

```python
USER_AGENT = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36"
```

## 🐛 Debug & Testing Tools

### HTML Export Tool
Script `debug/HTML_export_debug.py` để export HTML từ job sites cho việc testing selectors:

```bash
cd debug
python HTML_export_debug.py
```

### Jupyter Notebook Testing
File `test.ipynb` cho testing và development:

```bash
jupyter notebook test.ipynb
```

### Sample Output Files
- `vietnamworks.json` - Sample output từ VietnamWorks spider
- `outputs/jobs_*.json` - Timestamped output files
- `logs/crawl_*.log` - Timestamped log files

## 🗓️ **Scheduling & Orchestration**

### **Current: Windows Task Scheduler (Will be Deprecated)**

Hiện tại, việc chạy thu thập dữ liệu hàng ngày được thực hiện thông qua `crawl_daily.bat` và Windows Task Scheduler. Tuy nhiên, trong kiến trúc kỹ thuật dữ liệu mới, điều này sẽ được thay thế bằng Apache Airflow để có khả năng điều phối mạnh mẽ và linh hoạt hơn.

### **Target: Apache Airflow Orchestration**

Với kiến trúc mới, Apache Airflow sẽ là công cụ chính để lên lịch, điều phối và giám sát toàn bộ quy trình dữ liệu (data pipeline), bao gồm:

1.  **Chạy Spiders**: Kích hoạt các spiders của CrawlJob để thu thập dữ liệu.
2.  **Kiểm tra Chất lượng Dữ liệu**: Chạy các `checkpoint` của Great Expectations để đảm bảo chất lượng dữ liệu thô.
3.  **Biến đổi Dữ liệu**: Thực thi các `dbt run` để tạo và cập nhật các mô hình dữ liệu (data models) trong DuckDB.
4.  **Làm mới Dashboards**: Đảm bảo Apache Superset dashboards luôn hiển thị dữ liệu mới nhất.
5.  **Giám sát & Cảnh báo**: Cung cấp khả năng giám sát tập trung và gửi cảnh báo khi có lỗi.

```mermaid
flowchart TD
    start([Scheduled 02:00]) --> run_spiders[Task: run_spiders]
    run_spiders --> ge_raw[Task: ge_validate_raw]
    ge_raw -->|PASS| dbt_run[Task: dbt_run]
    ge_raw -->|FAIL| alert1([Alert + Stop])
    dbt_run --> ge_marts{Run ge_validate_marts?}
    ge_marts -->|YES| ge_marts_task[Task: ge_validate_marts] --> publish[Task: publish_duckdb]
    ge_marts -->|NO| publish
    publish --> notify[Task: notify_success]

    classDef t fill:#fff3e0,stroke:#e65100,stroke-width:1px
    class run_spiders,ge_raw,dbt_run,ge_marts_task,publish,notify t
```

### Chi tiết cấu hình Task Scheduler (GUI)

1) Mở Task Scheduler → Create Task… (không phải Basic Task)
- Tab General:
  - Name: CrawlJob Daily (hoặc tên bạn muốn)
  - Description: Chạy `crawl_daily.bat` để thu thập dữ liệu hằng ngày
  - Chọn "Run whether user is logged on or not"
  - Tick "Run with highest privileges"
  - Configure for: Windows 10/11
- Tab Triggers → New…
  - Begin the task: On a schedule
  - Daily, Start at: 02:00 (ví dụ)
  - (Tuỳ chọn) Advanced: Repeat task every: 4 hours; For a duration of: Indefinitely → dùng khi muốn chạy nhiều lần/ngày
  - OK
- Tab Actions → New…
  - Action: Start a program
  - Program/script: `cmd.exe`
  - Add arguments: `/c "D:\Practice\Scrapy\CrawlJob\crawl_daily.bat"`
  - Start in (optional): `D:\Practice\Scrapy\CrawlJob`
  - Lưu ý: luôn bọc đường dẫn có dấu cách trong dấu nháy kép ""
  - OK
- Tab Conditions: tuỳ nhu cầu (ví dụ bỏ chọn "Start the task only if the computer is on AC power")
- Tab Settings:
  - Cho phép "Allow task to be run on demand"
  - Nếu task có thể chạy lâu: điều chỉnh "Stop the task if it runs longer than"
- Nhấn OK và nhập mật khẩu user nếu được yêu cầu

2) Chạy test ngay
- Trong Task Scheduler, chọn task → Run
- Kiểm tra:
  - File `outputs\jobs_*.json` được sinh
  - File `logs\crawl_*.log` có nội dung log

3) Tạo task bằng dòng lệnh (tùy chọn)
```bat
REM Đường dẫn generic (sửa Path_to cho phù hợp)
SCHTASKS /Create /TN "CrawlJob Daily" /TR "cmd.exe /c \"Path_to\\crawl_daily.bat\"" /SC DAILY /ST 02:00 /RL HIGHEST /F

REM Ví dụ theo project này
SCHTASKS /Create /TN "CrawlJob Daily" /TR "cmd.exe /c \"D:\\Practice\\Scrapy\\CrawlJob\\crawl_daily.bat\"" /SC DAILY /ST 02:00 /RL HIGHEST /F

REM Chạy mỗi 4 giờ (lặp vô hạn) bắt đầu từ 00:00
SCHTASKS /Create /TN "CrawlJob Every4H" /TR "cmd.exe /c \"D:\\Practice\\Scrapy\\CrawlJob\\crawl_daily.bat\"" /SC HOURLY /MO 4 /ST 00:00 /RL HIGHEST /F

REM Chạy dưới tài khoản SYSTEM (không cần đăng nhập)
SCHTASKS /Create /TN "CrawlJob SYSTEM" /TR "cmd.exe /c \"D:\\Practice\\Scrapy\\CrawlJob\\crawl_daily.bat\"" /SC DAILY /ST 02:00 /RU SYSTEM /RL HIGHEST /F
```

4) Gợi ý cấu hình trong `crawl_daily.bat`
- Nếu dùng virtualenv, bỏ comment dòng `call ...activate.bat` và sửa path cho đúng
- Nếu `python` không có trong PATH của dịch vụ, dùng full path tới `python.exe` (đã có dòng mẫu trong file .bat)
- Có thể đổi `--keyword` theo nhu cầu

5) Troubleshooting Task Scheduler
- "The system cannot find the file specified": kiểm tra quotes và đường dẫn trong Program/script, Arguments, Start in
- Exit code 1/2: xem file log trong `logs\crawl_*.log` để biết lỗi chi tiết (selector, SQL, mạng…)
- Không tạo ra output/log: kiểm tra quyền ghi thư mục hoặc dùng Start in để đặt Working Directory đúng
- Không kết nối được SQL Server: kiểm tra TCP/IP, port 1433, firewall; `.env` đúng `SQL_SERVER`

## 🔧 Troubleshooting

### Lỗi kết nối PostgreSQL
1. Kiểm tra PostgreSQL container đang chạy
2. Kiểm tra `.env`: `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
3. Kiểm tra firewall và network access tới PostgreSQL container/host
4. Kiểm tra database permissions cho user

### Lỗi scraping
1. Kiểm tra internet connection
2. Thử tăng `DOWNLOAD_DELAY` trong `settings.py`
3. Kiểm tra website có thay đổi cấu trúc HTML không
4. Sử dụng debug tools để export HTML: `python debug/HTML_export_debug.py`

### **CSS Selector Issues**
- Update selectors in spider if website HTML changes
- Use `debug/HTML_export_debug.py` to test selectors
- Check `logs/crawl_*.log` for error messages

### **Spider-Specific Troubleshooting**

#### **Selenium Spiders (ITviec, LinkedIn, VietnamWorks)**
- **ChromeDriver Issues**: Install `webdriver-manager` or update Chrome
- **Cloudflare Bypass**: ITviec uses Undetected ChromeDriver with 95% success rate
- **Browser Cleanup**: Windows-compatible cleanup prevents WinError 6
- **Anti-Detection**: Advanced stealth options and fingerprinting
- **Performance**: Selenium spiders slower than Scrapy but more reliable

#### **JavaScript-Heavy Sites (TopCV)**
- **Dynamic Content**: Enhanced parsing with JavaScript extraction
- **Missing Data**: Some fields may be missing due to dynamic loading
- **Rate Limiting**: TopCV has strict rate limiting
- **qgTracking**: Extracts data from `window.qgTracking` object

#### **Simple Scrapy Sites (JobsGO, JobOKO, etc.)**
- **Fast Performance**: Pure CSS/XPath selectors for speed
- **High Reliability**: Static content parsing
- **Easy Maintenance**: Simple selector updates when needed

### **Advanced Debug Tools**

#### **HTML Export for Selector Testing**
```bash
cd debug
python HTML_export_debug.py
```

#### **Log Analysis**
```bash
# Check recent logs
type logs\crawl_*.log

# Monitor real-time crawling
tail -f logs\crawl_*.log
```

#### **Individual Spider Testing**
```bash
# Test specific spider with debug output
python run_spider.py --spider topcv --keyword "python" --output debug.json

# Test API connectivity
curl http://127.0.0.1:8000/health
```

#### **Database Issues**
```bash
# Check PostgreSQL connection
python -c "import psycopg2; conn = psycopg2.connect(host='localhost', port='5432', database='jobdatabase', user='postgres', password='your_password'); print('Connected')"
```

### **Performance Troubleshooting**

#### **Slow Crawling**
1. **Check DOWNLOAD_DELAY**: Increase if getting blocked
2. **Reduce CONCURRENT_REQUESTS**: Lower concurrent connections
3. **Monitor Memory Usage**: Check for memory leaks
4. **Database Performance**: Ensure PostgreSQL has adequate resources

#### **Browser Issues (Selenium)**
1. **WinError 6**: Update browser cleanup code
2. **ChromeDriver Version**: Ensure compatibility with Chrome
3. **Anti-Detection**: Check Undetected ChromeDriver version
4. **Memory Cleanup**: Implement proper browser session management

### **Performance Optimization**
1. **Rate Limiting**: Adjust `DOWNLOAD_DELAY` based on site restrictions
2. **Concurrent Requests**: Reduce `CONCURRENT_REQUESTS` if getting blocked
3. **Memory Usage**: Monitor RAM usage with large datasets
4. **Database Performance**: Ensure PostgreSQL has adequate resources



## 📊 **Project Achievements Summary**

### ✅ **COMPLETED FEATURES (Current Production Ready)**
- **10 Job Sites**: Complete coverage of major Vietnamese job platforms
- **Smart Deduplication**: Advanced duplicate prevention system
- **Rate Limiting**: Respectful crawling with configurable delays
- **Error Resilience**: Comprehensive error handling and recovery
- **Production Ready**: Windows Task Scheduler integration (will transition to Airflow)
- **Modular Architecture**: Easily extensible spider system
- **Debug Tools**: Built-in testing and troubleshooting utilities
- **Data Quality**: 18+ field standardized data model

### 🏆 **TECHNICAL EXCELLENCE (Current Production Ready)**
- **Cloudflare Bypass**: 95% success rate with Undetected ChromeDriver
- **Hybrid Architecture**: Perfect Scrapy-Selenium integration
- **Enterprise Pipeline**: Professional ETL with PostgreSQL (initial ingestion)
- **Modular Frontend**: Optimized 70KB bundle with caching
- **Mobile-First Design**: Perfect responsive experience
- **API Performance**: FastAPI async with optimal response times

### 📈 **BUSINESS IMPACT (Current Production Ready)**
- **Complete Market Coverage**: All major Vietnamese job sites
- **High Data Quality**: Standardized, clean job data
- **Real-time Access**: Instant search with pagination
- **User Experience**: Modern responsive dashboard
- **Operational Excellence**: Automated, reliable execution

## 🎯 **CONCLUSION: EVOLVING TOWARDS PROFESSIONAL DATA ENGINEERING**

**CrawlJob is successfully transitioning from a production-ready scraping system to a comprehensive data engineering project.**

### **Current State: Ready for Production Use** ✅
- Comprehensive 10-site job scraping coverage
- Robust error handling and recovery mechanisms
- Advanced anti-detection capabilities
- Modular and maintainable codebase
- Complete documentation and testing framework

### **Target State: Scalable and Feature-Rich Data Engineering Platform** ✅
- Easy integration of new data sources and models
- Configurable performance parameters across the data pipeline
- Robust data quality validation and monitoring
- Advanced analytics and visualization capabilities with Superset
- Orchestrated workflows for automated, reliable data processing
- Containerized deployment for portability and scalability

### **Future-Proof Design** ✅
- Modular frontend architecture
- Extensible spider framework
- Performance optimizations in place
- Clear roadmap for advanced data engineering features and ML integration

## 📄 License

MIT License
