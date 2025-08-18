# Project: CrawlJob

## 🎯 Current State
- **Phase**: Phase 2 in progress (FastAPI completed)
- **Progress**: 10/12 tasks completed
- **Next Goal**: Exporters and optimization improvements

## ✅ Completed Tasks
- [x] Implement spiders: JobsGO, JobOKO, 123job, CareerViet
- [x] SQL Server pipeline: create table if missing, insert items
- [x] CLI runner `run_spider.py` with FEEDS to export JSON
- [x] Environment-based DB configuration via `.env` (python-dotenv)
- [x] Basic throttling config and custom User-Agent
- [x] Dedup & Unique Constraint — unique on `(source_site, job_url)`; prevent duplicates (completed)
- [x] Upsert (Insert-or-Update) + `updated_at` — update existing rows and set `updated_at` (completed)
- [x] Structured Logging (được chủ dự án xác nhận bỏ qua và coi như hoàn tất)
- [x] API Read-Only Service (FastAPI) — implemented with /health and /jobs endpoints (completed)
- [x] Incremental Crawling & Scheduling — added `crawl_daily.bat` and README Scheduling section; supports daily runs with logs/outputs (completed)

## 🔄 Pending Tasks
### Phase 2: Web App MVP (HIGH PRIORITY)
- [ ] Exporters: CSV/Parquet (45 minutes)
  - **Objective**: Hỗ trợ xuất CSV/Parquet ngoài JSON.
  - **Why?**: Linh hoạt tích hợp BI/ML.
  - **Files to modify**: `run_spider.py` (tham số `--output-format`), README.
  - **Acceptance Criteria**: Tạo được file `.csv`/`.parquet` với schema ổn định.
  - **Test Cases**: So sánh số bản ghi giữa DB và file export.

### Phase 3: Optimization (MEDIUM PRIORITY)
- [ ] AutoThrottle & Rotating User-Agent/Proxies (1.5 hours)
  - **Objective**: Giảm rate-limit/ràng buộc bot.
  - **Why?**: Ổn định crawl khi quy mô lớn.
  - **Files to modify**: `settings.py` (AutoThrottle), middleware UA/proxy.
  - **Acceptance Criteria**: Giảm lỗi 429/ban; tốc độ crawl ổn định.
  - **Test Cases**: So sánh thời gian/ lỗi trước-sau.

- [ ] Selector Resilience (1.5 hours)
  - **Objective**: Chuẩn hoá selector theo module và fallback đa chiến lược.
  - **Why?**: Giảm vỡ khi HTML thay đổi nhỏ.
  - **Files to modify**: `spiders/` (trích chung hàm extract, regex labels), `utils.py`.
  - **Acceptance Criteria**: 90% trang thay đổi nhẹ vẫn parse được các trường chính.
  - **Test Cases**: Bộ trang mẫu (cũ/mới) parse ổn.

- [ ] Basic Tests (1 hour)
  - **Objective**: Thêm unit test cho utils và pipeline; fake HTML cho parser.
  - **Why?**: Bảo vệ chức năng cốt lõi.
  - **Files to modify**: `tests/` mới; CI cân nhắc sau.
  - **Acceptance Criteria**: `pytest` pass; coverage tối thiểu cho utils/pipeline.

### Phase 4: Advanced Features (LOW PRIORITY)
- [ ] Enrichment & NLP (4 hours)
  - **Objective**: Chuẩn hoá trường (mức lương, địa điểm), trích kỹ năng, phân loại ngành.
  - **Why?**: Tăng giá trị phân tích downstream.
  - **Files to modify**: Module `enrichment/` (chuẩn hoá, mapping, NLP cơ bản), thêm cột mới nếu cần.
  - **Acceptance Criteria**: Tỷ lệ parse chuẩn hoá >80% cho mẫu thử.

- [ ] Analytics Dashboard (2 hours)
  - **Objective**: Metabase/PowerBI/Streamlit dashboard nhanh.
  - **Why?**: Trực quan hoá số liệu.
  - **Files to modify**: Tài liệu cấu hình + script kết nối.
  - **Acceptance Criteria**: Xem được top công ty, mức lương theo vị trí.

## 📊 Workflow Visualization
```mermaid
graph TD
    subgraph "Phase 1: Quick Wins"
        A[Dedup & Unique] --> B[Upsert + updated_at]
        B --> C[Structured Logging]
    end
    subgraph "Phase 2: Core Implementation"
        C --> D[FastAPI Read API]
        D --> E[CSV/Parquet Export]
        E --> F[Incremental & Scheduling]
    end
    subgraph "Phase 3: Optimization"
        F --> G[AutoThrottle & Rotating UA/Proxies]
        G --> H[Selector Resilience]
        H --> I[Basic Tests]
    end
    subgraph "Phase 4: Advanced"
        I --> J[Enrichment & NLP]
        J --> K[Analytics Dashboard]
    end
```

## 🎯 Next Actions
1. Exporters CSV/Parquet
2. AutoThrottle optimization
3. Selector resilience + basic tests

## 📊 Progress Tracking
- **Total tasks**: 12
- **Completed**: 10
- **Remaining**: 2
- **Estimated time**: ~5.5–6 hours

## 🎯 Success Criteria
- [ ] Không còn trùng lặp theo `job_url` sau nhiều lần crawl
- [ ] Có API read-only để tiêu thụ dữ liệu
- [ ] Crawl ổn định với AutoThrottle và UA/Proxy
- [ ] Có test cơ bản bảo vệ pipeline và utils
