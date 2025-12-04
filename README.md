# CrawlJob - Vietnam Job Market Analytics Platform

Dự án thu thập, lưu trữ và phân tích dữ liệu việc làm nghành data từ các trang tuyển dụng lớn tại Việt Nam (TopCV, Linkedin, ITViec, JobStreet, v.v.). Hệ thống được thiết kế theo kiến trúc Hybrid, tách biệt giữa nhu cầu truy xuất nhanh cho ứng dụng (OLTP) và nhu cầu phân tích dữ liệu lớn (OLAP).

## 🏗 Kiến Trúc Hệ Thống (Architecture)

Mô hình tổng quan luồng dữ liệu (Data Flow):

```mermaid
graph TB
    subgraph Scheduling_Layer["🗓️ Scheduling Layer"]
        subgraph GitHub_Actions["☁️ GitHub Actions (Cloud Server)"]
            GA_CRON["⏰ Cron Schedule<br/>*/6 * * * *"]
            GA_TOPCV["🕷️ 123Job Spider"]
            GA_VNW["🕷️ VietnamWorks Spider"]
            GA_SCRIPT["📜 Python Script<br/>scrape_easy.py"]
        end
        
        subgraph Airflow_Local["🏠 Apache Airflow (Local Server)"]
            AF_DAG["📋 DAG: scrape_hard_sites<br/>0 2 * * *"]
            AF_LINKEDIN["🕷️ LinkedIn Spider"]
            AF_GLASSDOOR["🕷️ TopCV Spider"]
            AF_ANTIBOT["🛡️ Anti-bot Handler<br/>Proxy + Rotating UA"]
            AF_SCRIPT["📜 Python Script<br/>scrape_hard.py"]
        end
    end

    subgraph Collection_Layer["🔍 Collection Layer"]
        A["🕸️ Scrapy Spiders"]
    end

    subgraph OLTP_Staging["💾 OLTP / Staging (Supabase)"]
        B[("📥 staging_jobs")]
        B3[("⚠️ quarantine_jobs")]
        B2[("✅ jobs")]
        B1["🖥️ Web App Backend"]
    end

    subgraph Orchestration["⚙️ Orchestration (Airflow)"]
        C1["📤 Task: Extract"]
        C2["✔️ Task: Validate DQ"]
        C3["🔄 Task: Upsert"]
        C4["📦 Task: Load to DW"]
    end

    subgraph OLAP_DW["📊 OLAP / Data Warehouse (BigQuery)"]
        D1[("🗃️ raw_jobs")]
        D2[("🏷️ dim_skills")]
        D3[("📈 fact_market_trends")]
    end

    subgraph User_Interface["👤 User Interface"]
        E["🌐 Job Search Website"]
        F["📊 BI Dashboard"]
    end

    %% GitHub Actions Flow
    GA_CRON --> GA_TOPCV
    GA_CRON --> GA_VNW
    GA_TOPCV --> GA_SCRIPT
    GA_VNW --> GA_SCRIPT
    GA_SCRIPT --> A

    %% Airflow Local Flow
    AF_DAG --> AF_LINKEDIN
    AF_DAG --> AF_GLASSDOOR
    AF_LINKEDIN --> AF_ANTIBOT
    AF_GLASSDOOR --> AF_ANTIBOT
    AF_ANTIBOT --> AF_SCRIPT
    AF_SCRIPT --> A

    %% Collection to Staging
    A -->|"Insert Raw"| B
    
    %% ETL Pipeline
    C1 -->|"Read"| B
    C1 --> C2
    C2 -->|"PASS ✅"| C3
    C2 -->|"FAIL ❌"| B3
    C3 -->|"Upsert"| B2
    C3 --> C4
    C4 -->|"Batch Load"| D1
    
    %% Backend & UI
    B2 <-->|"Read/Write"| B1
    B1 --> E
    
    %% Data Warehouse Transform
    D1 --> D2
    D1 --> D3
    D3 --> F

    %% Styling
    classDef github fill:#24292e,stroke:#ffffff,color:#ffffff
    classDef airflow fill:#017cee,stroke:#ffffff,color:#ffffff
    classDef scrapy fill:#60a839,stroke:#ffffff,color:#ffffff
    classDef supabase fill:#3ecf8e,stroke:#ffffff,color:#ffffff
    classDef bigquery fill:#4285f4,stroke:#ffffff,color:#ffffff
    classDef ui fill:#ff6b6b,stroke:#ffffff,color:#ffffff

    class GA_CRON,GA_TOPCV,GA_VNW,GA_SCRIPT github
    class AF_DAG,AF_LINKEDIN,AF_GLASSDOOR,AF_ANTIBOT,AF_SCRIPT airflow
    class A scrapy
    class B,B2,B3,B1 supabase
    class D1,D2,D3 bigquery
    class E,F ui
```

### Chi tiết các thành phần:

1.  **Collection Layer (Scrapy):**
    *   Nhiệm vụ: Thu thập dữ liệu từ các nguồn job board.
    *   Đầu ra: Dữ liệu thô được làm sạch cơ bản.
    *   Destination: Ghi trực tiếp vào bảng `staging_jobs` trên Supabase.

2.  **OLTP Layer (Supabase - PostgreSQL):**
    *   Vai trò: Operational Database & Staging Area.
    *   Chức năng: 
        *   Lưu trữ dữ liệu "nóng" (việc làm đang tuyển, dữ liệu mới nhất).
        *   Cung cấp API cho **Website tra cứu việc làm**.
        *   Tận dụng tính năng Realtime/Auth của Supabase để xây dựng App nhanh chóng.

3.  **Orchestration Layer (Airflow):**
    *   Vai trò: Điều phối luồng dữ liệu (ETL Pipeline).
    *   Nhiệm vụ:
        *   Lên lịch chạy Spider định kỳ.
        *   **Sync Job:** Query dữ liệu mới từ Supabase -> Load vào Google BigQuery (Batch processing).

4.  **OLAP Layer (Google BigQuery):**
    *   Vai trò: Data Warehouse (Kho dữ liệu phân tích).
    *   Chức năng:
        *   Lưu trữ lịch sử dài hạn (Historical Data).
        *   Xử lý các truy vấn nặng: Phân tích xu hướng lương, kỹ năng hot, biến động thị trường.
        *   Nguồn dữ liệu cho các báo cáo Insight (Looker Studio, Metabase).

## 📂 Cấu Trúc Thư Mục (Project Structure)

```text
CrawlJob/
├── airflow/                # Airflow DAGs & Configuration
│   └── dags/
│       ├── sync_supabase_bigquery.py  # ETL: Supabase -> BigQuery
│       └── trigger_spiders.py         # Schedule Scrapy Jobs
├── api/                    # Backend API (nếu cần custom logic ngoài Supabase)
├── CrawlJob/               # Scrapy Project Core
│   ├── spiders/            # Các Spider thu thập dữ liệu
│   ├── items.py            # Định nghĩa cấu trúc dữ liệu (Data Models)
│   ├── pipelines.py        # Xử lý dữ liệu trước khi lưu vào Supabase
│   └── settings.py         # Cấu hình Scrapy (Delay, User-Agent, DB Connect)
├── notebooks/              # Jupyter Notebooks (EDA, Data Analysis, Test DuckDB/BQ)
├── scripts/                # Utility Scripts (Chạy spider thủ công, helper tools)
├── web/                    # Frontend (Website tra cứu việc làm đơn giản)
├── docker-compose.yml      # Setup môi trường (Airflow, Local DB...)
├── requirements.txt        # Python Dependencies
└── README.md               # Project Documentation
```

## 🚀 Getting Started

### 1. Prerequisites
*   Python 3.10+
*   Docker & Docker Compose (cho Airflow)
*   Tài khoản Supabase & Google Cloud Platform (BigQuery API enabled)

### 2. Setup Environment
```bash
# Clone project
git clone <repo-url>
cd CrawlJob

# Tạo môi trường ảo
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Cài đặt thư viện
pip install -r requirements.txt
```

### 3. Configuration (.env)
Tạo file `.env` từ `env.example` và điền các thông tin credentials:
```ini
# Supabase
SUPABASE_URL=...
SUPABASE_KEY=...
DB_CONNECTION_STRING=postgresql://user:pass@host:port/dbname

# Google Cloud (BigQuery)
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
BQ_PROJECT_ID=...
BQ_DATASET_ID=...
```


