# CrawlJob Project - Silver Layer Architecture

## Tổng quan dự án
CrawlJob là một dự án Scrapy crawl dữ liệu job từ nhiều job boards Vietnam (JobOKO, TopCV, VietnamWorks, ITviec, LinkedIn, CareerLink, CareerViet, Job123, JobsGo, JobStreet).

## Kiến trúc data pipeline

### Bronze Layer
- Source: PostgreSQL database với bảng `jobs`
- Chứa raw data từ tất cả sources
- Field `source_site` để phân biệt nguồn

### Silver Layer - Source-Specific Staging (MỚI - Oct 2025)

**Kiến trúc:**
```
bronze.jobs → staging/stg_{source}_jobs.sql → stg_jobs_unified.sql → Gold layer
```

**Staging models theo source:**
1. `stg_joboko_jobs.sql` - JobOKO specific logic
2. `stg_topcv_jobs.sql` - TopCV specific logic  
3. `stg_vietnamworks_jobs.sql` - VietnamWorks specific logic
4. Template: `stg_itviec_jobs.sql.template` cho source mới

**Unified model:**
- `stg_jobs_unified.sql` - Union tất cả source-specific models

**Lý do thiết kế:**
- Mỗi job site có format dữ liệu khác nhau (salary, experience, education)
- Tách riêng giúp dễ maintain khi một site thay đổi
- Testing cụ thể cho từng source
- Performance tốt hơn với incremental per source

### Helper Macros
File: `macros/normalize_job_fields.sql`
- `normalize_salary(column, source_type)` - Chuẩn hóa lương
- `normalize_experience(column, source_type)` - Chuẩn hóa kinh nghiệm
- `clean_whitespace(column)` - Trim và remove extra spaces
- `normalize_deadline(column)` - Format ngày deadline

### Testing Strategy
- Unique key: `job_url` per source
- Not null checks: job_title, company_name, source_site
- Accepted values: source_name
- Custom tests: deadline_after_scraped, is_recent, valid_url
- Data completeness monitoring

### Gold Layer
Chưa được triển khai chi tiết, nhưng sẽ consume từ `stg_jobs_unified`

## Config quan trọng

**Incremental strategy:**
- materialized: incremental
- unique_key: job_url
- incremental_strategy: merge
- Filter: `scraped_at > max(scraped_at)`

**Schema:**
- Bronze: `bronze` schema
- Silver: `silver` schema
- Models nằm trong folder `models/silver/staging/`

## Data Quality
File: `analyses/staging_quality_check.sql`
- Row counts per source
- Completeness percentage
- Duplicate detection  
- Quality issues (short titles, missing descriptions, etc.)

## Cách sử dụng

**Build staging:**
```bash
dbt run --select tag:staging
dbt run --select stg_jobs_unified
```

**Test:**
```bash
dbt test --select tag:staging
```

**Thêm source mới:**
1. Copy template `stg_itviec_jobs.sql.template`
2. Customize logic cho source
3. Add to `stg_jobs_unified.sql`
4. Update `schema.yml`

## Deprecated
- `stg_jobs.sql` - Model cũ, giữ lại để backward compatible
- Nên dùng `stg_jobs_unified.sql` thay thế

## Documentation
- `IMPLEMENTATION_SUMMARY.md` - Tổng hợp implementation
- `README.md` - Hướng dẫn sử dụng
- `MIGRATION.md` - Migration guide từ model cũ
- `schema.yml` - Tests và column descriptions
