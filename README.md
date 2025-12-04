# CrawlJob - Vietnam Job Market Analytics Platform

Dự án thu thập, lưu trữ và phân tích dữ liệu việc làm nghành data từ các trang tuyển dụng lớn tại Việt Nam (TopCV, Linkedin, ITViec, JobStreet, v.v.). Hệ thống được thiết kế theo kiến trúc Hybrid, tách biệt giữa nhu cầu truy xuất nhanh cho ứng dụng (OLTP) và nhu cầu phân tích dữ liệu lớn (OLAP).

## 🏗 Kiến Trúc Hệ Thống (Architecture)

Mô hình tổng quan luồng dữ liệu (Data Flow):

```mermaid
graph LR
    subgraph "Collection Layer"
        A[Scrapy Spiders] 
    end

    subgraph "OLTP / Staging (Supabase)"
        B[(Table: staging_jobs)]
        B1[Web App Backend]
    end

    subgraph "Orchestration (Airflow)"
        C[ETL DAGs]
    end

    subgraph "OLAP / Data Warehouse (BigQuery)"
        D[(Dataset: job_market)]
        D1[Table: raw_jobs]
        D2[Table: dim_skills]
        D3[Table: fact_market_trends]
    end

    subgraph "User Interface"
        E[Job Search Website]
        F[BI Reports / Dashboard]
    end

    %% Flows
    A -->|Upsert Raw Data| B
    B <-->|Read/Write Hot Data| B1
    B1 --> E
    
    C -->|Extract New Data (Daily)| B
    C -->|Batch Load| D1
    
    D1 -->|SQL Transform| D2
    D1 -->|SQL Transform| D3
    
    D3 --> F
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

## 📊 Roadmap
- [x] Xây dựng Scrapy Spider cơ bản.
- [x] Thiết lập lưu trữ Staging trên Supabase.
- [ ] Xây dựng luồng Airflow Sync dữ liệu sang BigQuery.
- [ ] Phát triển Web UI tra cứu đơn giản.
- [ ] Xây dựng Dashboard phân tích Insight trên BigQuery.

