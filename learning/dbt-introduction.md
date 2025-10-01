# Giới thiệu về dbt (data build tool)

dbt (data build tool) là một công cụ mã nguồn mở mạnh mẽ dùng để biến đổi dữ liệu (data transformation) trong data warehouse, giúp các data engineer và analytics engineer xây dựng data pipeline theo nguyên tắc software engineering. Nó sử dụng SQL và Jinja templating để mô hình hóa dữ liệu, hỗ trợ nhiều data platforms như PostgreSQL, Snowflake, BigQuery, DuckDB, Redshift, và hơn thế. Dưới đây là tổng quan toàn diện về những gì dbt có thể làm, dựa trên tài liệu chính thức. Nội dung được phân loại theo các tính năng chính để dễ theo dõi.

## 1. Xây dựng và Quản lý Data Models
- **Models**: Tạo các data models (bảng, view, incremental tables) từ nguồn dữ liệu. Các file SQL được đặt trong thư mục `models/`, dbt sẽ compile và execute chúng để tạo ra dữ liệu sạch, chuẩn hóa.
  - Materializations: View (chỉ query), Table (vật lý hóa), Incremental (chỉ xử lý dữ liệu mới), Ephemeral (chạy inline mà không lưu), và các tùy chỉnh.
  - Incremental Strategies: Append (thêm mới), Merge (hợp nhất dựa trên key), Delete+Insert (xóa và thêm), Insert Overwrite (ghi đè partition), Microbatch (cho streaming).
- **Sources**: Định nghĩa nguồn dữ liệu (tables từ warehouse) trong YAML (`sources.yml`), giúp track freshness (tươi mới) và lineage (dòng chảy dữ liệu).
- **Seeds**: Quản lý dữ liệu tĩnh (CSV files) như lookup tables, dbt sẽ load chúng thành tables trong warehouse.
- **Snapshots**: Theo dõi thay đổi dữ liệu theo thời gian (SCD Type 2), phát hiện thêm/sửa/xóa records và lưu lịch sử với metadata (dbt_valid_from, dbt_valid_to).
  - Strategies: Timestamp (dựa cột updated_at) hoặc Check (dựa các cột cụ thể).

## 2. Kiểm tra và Đảm bảo Chất lượng Dữ liệu (Data Quality)
- **Built-in Tests**: Hàng chục test sẵn có như unique, not_null, accepted_values, relationships, freshness.
- **Custom Tests**: Viết test SQL tùy chỉnh trong thư mục `tests/`.
- **Singular/Generic Tests**: Áp dụng test cho models/sources qua YAML (schema.yml).
- **dbt Expectations**: Tích hợp Great Expectations để test phức tạp hơn (như dbt-expectations package).
- **Freshness Checks**: Kiểm tra dữ liệu nguồn có "tươi" không (dựa thời gian load).

## 3. Tái sử dụng Code và Configuration
- **Macros**: Viết Jinja macros (SQL snippets) trong `macros/` để tái sử dụng, như format date, generate surrogate keys, hoặc custom logic.
- **Packages**: Quản lý dependencies qua `packages.yml` (dbt hub), cài đặt packages như dbt-utils (macros tiện ích), dbt-expectations (test nâng cao).
- **Variables**: Định nghĩa vars trong `dbt_project.yml` để parameterize (ví dụ: start_date cho queries).
- **Configs**: Cấu hình linh hoạt qua YAML hoặc inline Jinja, như schema, database, tags, materialization cho từng model/snapshot.

## 4. Documentation và Visualization
- **Auto-generated Docs**: Chạy `dbt docs generate` để tạo docs từ YAML descriptions và code comments. Xem qua `dbt docs serve` (web interface) với lineage graph (dag visualize dependencies).
- **YAML Descriptions**: Thêm description, tags, meta cho models/columns/sources trong schema.yml.
- **Custom Docs Blocks**: Viết docs Jinja (như `__overview__`) để tùy chỉnh trang overview.
- **Semantic Models**: Định nghĩa metrics, dimensions, entities trong YAML để tích hợp với BI tools (Tableau, Looker, Google Sheets).

## 5. CLI Commands và Workflow
- **Core Commands**:
  - `dbt run`: Compile và execute models.
  - `dbt test`: Chạy tests.
  - `dbt build`: Run + test + snap + seed (tất cả trong một).
  - `dbt compile`: Chỉ compile SQL (không execute).
  - `dbt snapshot`: Chạy snapshots.
  - `dbt seed`: Load seeds.
  - `dbt docs generate/serve`: Tạo và xem docs.
  - `dbt ls`: List resources.
  - `dbt clean`: Xóa cache.
  - `dbt deps`: Cài packages.
  - `dbt source freshness`: Kiểm tra freshness.
- **Node Selection**: Sử dụng `--select`, `--exclude` với syntax mạnh mẽ (tags, paths, @parents/children, +descendants) để chạy subset models.
- **State Management**: So sánh state giữa runs (previous run artifacts) để incremental builds.
- **RPC/CLI Integration**: Hỗ trợ RPC cho automation.

## 6. Semantic Layer và Metrics
- **Metrics Layer**: Định nghĩa measures (sum, count), dimensions (categorical/time), entities (join keys) trong semantic models.
- **API Access**: GraphQL/JDBC APIs để query metrics từ apps/BI tools, đảm bảo consistency và governance.
- **Integrations**: Kết nối với Hex, Mode, Lightdash, Google Sheets, Tableau.

## 7. Deployment và Collaboration
- **dbt Cloud**: Phiên bản hosted với scheduling, CI/CD (Git integration), environments (dev/prod), job orchestration, web IDE, notifications (webhooks/Slack).
- **dbt Core**: Chạy local qua CLI, tích hợp Airflow, Dagster cho orchestration.
- **Profiles**: Quản lý connections (profiles.yml) cho nhiều targets (dev/prod).
- **Git Integration**: Branching strategies cho dev/QA/prod.

## 8. Adapters và Extensions
- **Adapters**: Hỗ trợ 20+ platforms (Snowflake, BigQuery, Databricks, DuckDB, Trino, ClickHouse, etc.) qua dbt-labs/dbt-adapters.
- **Custom Adapters/Strategies**: Viết macro tùy chỉnh cho incremental hoặc materializations.
- **Packages Ecosystem**: Hàng trăm packages trên dbt hub cho analytics (như dbt_product_analytics cho funnel/retention).

## 9. Best Practices và Scalability
- **Project Structure**: Tổ chức theo layers (staging > intermediate > marts) để ELT pipeline sạch sẽ.
- **Versioning**: Model versions với include/exclude columns.
- **Logs và Debugging**: Logs chi tiết (JSON/text formats), debug mode.
- **Performance**: Full/partial parsing, threads cho concurrency, cache cho compile.

## Hạn chế và Lưu ý
- dbt tập trung vào transformation (T trong ELT), không load/extract dữ liệu (dùng Airbyte/Fivetran cho E/L).
- Không hỗ trợ real-time/streaming native (nhưng có microbatch cho gần real-time).
- Yêu cầu data warehouse để chạy (không phải file-based thuần).