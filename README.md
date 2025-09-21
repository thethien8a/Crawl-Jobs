# CrawlJob - Professional Data Engineering Project 🎉

Hệ thống kỹ thuật dữ liệu chuyên nghiệp để thu thập, kiểm tra chất lượng, biến đổi và trực quan hóa dữ liệu việc làm từ **10 trang tuyển dụng hàng đầu Việt Nam**. Dự án này không chỉ là một công cụ scraping mà còn là một pipeline dữ liệu hoàn chỉnh, sẵn sàng cho các tác vụ phân tích và học máy.

## 🏗️ Kiến trúc Hệ thống

Dự án được xây dựng theo kiến trúc hiện đại, tách biệt rõ ràng các thành phần, bao gồm:
- **Thu thập dữ liệu (Ingestion)**: `Scrapy` & `Selenium` & `BeautifulSoup`
- **Điều phối (Orchestration)**: `Apache Airflow`
- **Lưu trữ (Storage)**: `PostgreSQL` (OLTP) & `DuckDB` (OLAP)
- **Kiểm tra chất lượng (Data Quality)**: `Soda Core` (Raw gating) + `dbt tests` (Business rules)
- **Đồng bộ Postgres → DuckDB (EL)**: `DuckDB postgres_scanner` (không cần Docker/Airbyte)
- **Biến đổi dữ liệu (Transformation)**: `dbt-duckdb` (biến đổi trong DuckDB)
- **API & Giao diện (Presentation)**: `FastAPI` & `Vanilla JS`
- **Trực quan hóa (BI)**: `Apache Superset`

```mermaid
flowchart TD
    subgraph ingestion["🔄 Data Ingestion"]
        spiders["🕷️ CrawlJob Spiders"]
        airflow["⚡ Apache Airflow"]
    end
    subgraph storage["💾 Data Storage"]
        postgres["🐘 PostgreSQL (OLTP)"]
        duckdb["🦆 DuckDB (OLAP)"]
    end
    subgraph processing["⚙️ Data Processing"]
        soda["🧪 Soda Core (Gate Raw)"]
        scanner["🔌 DuckDB postgres_scanner (Sync)"]
        dbt["🔨 dbt-duckdb (Transform + Tests)"]
    end
    subgraph presentation["📊 Presentation & Access"]
        superset["Apache Superset (BI)"]
        fastapi["🚀 FastAPI (API)"]
        webapp["🌐 Web App"]
    end
    airflow --> spiders --> postgres
    airflow --> soda --> postgres
    airflow --> scanner --> duckdb
    airflow --> dbt
    dbt --> duckdb
    fastapi --> postgres
    webapp --> fastapi
    superset --> duckdb
```

## 🚀 Bắt đầu nhanh (Getting Started)

### Yêu cầu
- Python 3.10+
- Docker & Docker Compose (chỉ cho Postgres local)
- Git

### Cài đặt & Cấu hình

Thực hiện các bước sau theo đúng thứ tự để cài đặt môi trường development.

**1. Clone Repository**
```bash
git clone <your-repository-url>
cd CrawlJob
```

**2. Tạo và kích hoạt Môi trường ảo**
```bash
# Tạo môi trường ảo
python -m venv .venv

# Kích hoạt (Windows)
.\.venv\Scripts\activate
```

**3. Cài đặt các gói phụ thuộc**
```bash
pip install -r requirements.txt
```

**4. Cấu hình Biến môi trường**
Copy file `.env.example` thành file `.env` và điền các thông tin cần thiết.
```bash
# Windows
copy .env.example .env
```
Sau đó, mở file `.env` và điền thông tin đăng nhập PostgreSQL, đường dẫn DUCKDB_PATH, v.v.

**5. Khởi động Database**
Dự án sử dụng PostgreSQL chạy trong Docker. Hãy khởi động container:
```bash
docker-compose up -d
```
Lệnh này sẽ khởi động một service PostgreSQL có thể truy cập tại `localhost:5432`.

**6. Chạy thử nghiệm**
Bây giờ bạn đã sẵn sàng! Hãy thử chạy một spider để kiểm tra:
```bash
python run_spider.py --spider itviec --keyword "Data Engineer"
```
Dữ liệu sẽ được thu thập và lưu vào database PostgreSQL của bạn.

## 📖 Hướng dẫn sử dụng

### Chạy Spiders
Sử dụng script `run_spider.py` để thực thi việc thu thập dữ liệu.

```bash
# Chạy một spider cụ thể
python run_spider.py --spider topcv --keyword "Product Manager"

# Chạy tất cả 10 spiders
python run_spider.py --spider all --keyword "IT"
```

### Chạy API Server
API cung cấp dữ liệu đã thu thập cho giao diện web.
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```
- **Health check**: `http://localhost:8000/health`
- **Tìm kiếm jobs**: `http://localhost:8000/jobs?keyword=python`

### Kiểm tra chất lượng dữ liệu (Data Quality)
Áp dụng mô hình kiểm tra hai lớp + đồng bộ:

- Lớp 1 (Raw Gating - Soda Core): kiểm tra bảng `raw` ngay sau khi crawl để đảm bảo dữ liệu sẵn sàng.
```bash
# Ví dụ (chạy thủ công)
soda scan -d job_database -c soda/configuration.yml soda/checks/raw_jobs_check1.yml
soda scan -d job_database -c soda/configuration.yml soda/checks/raw_jobs_check2.yml
soda scan -d job_database -c soda/configuration.yml soda/checks/raw_jobs_check3.yml
```

- Đồng bộ (EL) sang DuckDB: dùng DuckDB postgres_scanner (script `scripts/sync_pg_to_duckdb.py`).
```bash
# Full refresh
set SYNC_MODE=full & python scripts/sync_pg_to_duckdb.py
# Incremental theo cột scraped_at (mặc định)
python scripts/sync_pg_to_duckdb.py
```

- Lớp 2 (Business Validation - dbt tests): chạy các kiểm tra cho các model sau khi `dbt run` trong DuckDB.
```bash
# Ví dụ với dbt-duckdb
cd path/to/dbt_duckdb_project
 dbt run && dbt test
```

## 🛠️ Công nghệ sử dụng

- **Scrapy & Selenium**: Lõi thu thập dữ liệu, với khả năng vượt qua Cloudflare.
- **PostgreSQL & Docker**: Lưu trữ dữ liệu thô, dễ dàng cài đặt và quản lý.
- **DuckDB postgres_scanner**: Đồng bộ trực tiếp Postgres → DuckDB, không cần Docker cho connector.
- **Soda Core + dbt tests**: Đảm bảo tính toàn vẹn và chất lượng dữ liệu (raw + transformed).
- **FastAPI**: Xây dựng API hiệu năng cao.
- **Và các công cụ khác trong DE Stack**: Airflow, dbt, DuckDB, Superset.

## 🤝 Đóng góp
Nếu bạn có ý tưởng cải thiện dự án, đừng ngần ngại tạo Pull Request hoặc mở một Issue.
