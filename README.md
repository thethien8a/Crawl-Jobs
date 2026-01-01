# Job Crawling & Analytics Data Pipeline Plan

## 1. Tổng quan dự án (Project Overview)
Dự án xây dựng hệ thống thu thập dữ liệu việc làm (Job Crawling), làm sạch và chuẩn hóa để phục vụ hai mục đích chính:
1.  **Web App Job Search**: Cung cấp API dữ liệu sạch, chuẩn hóa cho ứng dụng tìm kiếm việc làm.
2.  **Analytics Dashboard**: Cung cấp dữ liệu mô hình Dim/Fact để phân tích xu hướng thị trường lao động.

## 2. Kiến trúc dữ liệu (Data Architecture)
Dự án sử dụng kiến trúc **ELT (Extract - Load - Transform)** tập trung hoàn toàn trên **Supabase (PostgreSQL)**.

### Mô hình Medallion (Bronze -> Silver -> Gold)
Dữ liệu sẽ được tổ chức thành 3 tầng (Schemas) riêng biệt trong cùng một Database Supabase:

| Tầng (Layer) | Schema Name | Vai trò | Mô tả |
| :--- | :--- | :--- | :--- |
| **Bronze** | `raw_data` | **Raw / Staging** | Chứa dữ liệu thô nguyên bản từ Scrapy. Chấp nhận duplicate, null, lỗi format. Là nơi đổ dữ liệu đầu vào. |
| **Silver** | `app_layer` | **Clean / Serving** | Dữ liệu đã được làm sạch, deduplicate, chuẩn hóa (lương, địa điểm, kỹ năng). **Dùng cho Web App API**. |
| **Gold** | `analytics_dw` | **Analytics / Mart** | Dữ liệu được mô hình hóa dạng **Star Schema** (Dim/Fact). Tối ưu cho truy vấn báo cáo. **Dùng cho Dashboard**. |

## 3. Công nghệ sử dụng (Tech Stack)

*   **Ingestion (Thu thập):** Python Scrapy.
*   **Data Warehouse:** Supabase (PostgreSQL).
*   **Transformation (Biến đổi):** **dbt (data build tool)**.
*   **Orchestration (Điều phối):** Airflow (điều phối chỉnh) và GitHub Actions (chỉ để chạy scripts thu thập dữ liệu định kỳ)
*   **Visualization:** PowerBI 

## 4. Chi tiết triển khai (Implementation Plan)

### Bước 1: Thiết lập Database (Supabase)
Tạo các schema cần thiết để phân tách dữ liệu:
```sql
CREATE SCHEMA IF NOT EXISTS raw_data;
CREATE SCHEMA IF NOT EXISTS app_layer;
CREATE SCHEMA IF NOT EXISTS analytics_dw;
```

### Bước 2: Ingestion (Scrapy -> Raw)
*   Spider cào dữ liệu và lưu vào bảng trong schema `raw_data` (ví dụ: `raw_data.jobs_raw`).
*   Giữ nguyên logic cào hiện tại, chỉ thay đổi đích đến là bảng raw.

### Bước 3: Transformation (dbt)
Sử dụng **dbt** để quản lý toàn bộ logic biến đổi SQL.

#### 3.1. Bronze to Silver (Raw -> App)
*   **Mục tiêu:** Làm sạch dữ liệu để Web App sử dụng.
*   **Các tác vụ:**
    *   **Deduplication:** Loại bỏ tin tuyển dụng trùng lặp (dựa trên URL hoặc Title + Company).
    *   **Standardization:**
        *   Lương: Parse text "10-20 triệu" -> `min_salary: 10000000`, `max_salary: 20000000`.
        *   Địa điểm: Map "TP.HCM", "Hồ Chí Minh" -> "Ho Chi Minh".
    *   **Validation:** Loại bỏ các bản ghi rác, thiếu thông tin quan trọng.
*   **Output:** Bảng `app_layer.jobs`.

#### 3.2. Silver to Gold (App -> Analytics)
*   **Mục tiêu:** Xây dựng Data Mart cho Dashboard.
*   **Mô hình Star Schema:**
    *   **Fact Table:** `analytics_dw.fact_job_posts` (Chứa các metric, khóa ngoại).
    *   **Dimension Tables:**
        *   `analytics_dw.dim_company` (Thông tin công ty).
        *   `analytics_dw.dim_location` (Địa điểm).
        *   `analytics_dw.dim_date` (Ngày tháng).
        *   `analytics_dw.dim_industry` (Ngành nghề).
        *   `analytics_dw.dim_skills` (Kỹ năng yêu cầu).

## 5. Phát triển tương lai:
- Lấy thêm dữ liệu "quy mô công ty" (company size) từ các trang web: joboko, topcv, linkedin, 123job, careerlink, itviec