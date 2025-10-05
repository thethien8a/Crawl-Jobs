# Source-Specific Staging Models - Implementation Summary

## 📋 Tổng quan

Đã triển khai kiến trúc staging layer theo pattern **source-specific models** để xử lý dữ liệu từ nhiều job sites khác nhau một cách tối ưu.

## 📁 Cấu trúc files đã tạo

```
dbt_crawjob/
├── models/
│   └── silver/
│       ├── stg_jobs.sql (deprecated - giữ lại để backward compatible)
│       ├── stg_jobs_unified.sql (NEW - model chính)
│       └── staging/
│           ├── README.md
│           ├── MIGRATION.md
│           ├── schema.yml
│           ├── stg_joboko_jobs.sql
│           ├── stg_topcv_jobs.sql
│           ├── stg_vietnamworks_jobs.sql
│           └── stg_itviec_jobs.sql.template (template cho source mới)
├── macros/
│   └── normalize_job_fields.sql (helper macros)
└── analyses/
    └── staging_quality_check.sql (data quality queries)
```

## 🎯 Kiến trúc Data Flow

```
┌─────────────────┐
│  bronze.jobs    │ (Raw data từ tất cả sources)
└────────┬────────┘
         │
    ┌────┴────┐
    │ Filter  │ by source_site
    └────┬────┘
         │
    ┌────┴─────────────────────────────────┐
    │                                      │
    ▼                                      ▼
┌────────────────┐               ┌──────────────────┐
│ stg_joboko_*   │               │ stg_topcv_*      │
│ (JobOKO logic) │               │ (TopCV logic)    │
└───────┬────────┘               └────────┬─────────┘
        │                                 │
        │         ┌──────────────────┐    │
        └────────►│ stg_vietnamworks_│◄───┘
                  │ (VNW logic)      │
                  └────────┬─────────┘
                           │
                    UNION ALL
                           │
                           ▼
                  ┌─────────────────┐
                  │ stg_jobs_unified│
                  │ (Final staging) │
                  └────────┬────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ Gold Layer  │
                    └─────────────┘
```

## ✨ Features chính

### 1. Source-Specific Cleaning Logic

**stg_joboko_jobs.sql:**
- Xử lý salary format: "Thỏa thuận" → "Negotiable"
- Clean location: Remove "Khu vực:" prefix
- Normalize experience: "Dưới 1 năm" → "< 1 year"

**stg_topcv_jobs.sql:**
- Handle brand URLs vs regular URLs
- Education level standardization: "Đại học" → "Bachelor"
- Salary với USD support

**stg_vietnamworks_jobs.sql:**
- Salary: "You'll love it" → "Attractive"
- English experience levels: "Experienced", "Manager", etc.
- USD currency handling

### 2. Reusable Macros

File: `macros/normalize_job_fields.sql`

```sql
{{ normalize_salary('salary', 'joboko') }}
{{ normalize_experience('experience_level', 'topcv') }}
{{ clean_whitespace('job_title') }}
{{ normalize_deadline('job_deadline') }}
```

### 3. Comprehensive Testing

File: `staging/schema.yml`

- ✅ Unique job_url per source
- ✅ Not null checks cho required fields
- ✅ Accepted values cho source_name
- ✅ Data freshness checks
- ✅ Custom tests (deadline_after_scraped, etc.)

### 4. Data Quality Monitoring

File: `analyses/staging_quality_check.sql`

8 queries để monitor:
1. Jobs count per source
2. Salary types distribution
3. Experience levels
4. Data completeness percentage
5. Duplicate detection
6. Top companies
7. Recent scraping activity
8. Quality issues detection

## 🚀 Cách sử dụng

### Build tất cả staging models

```bash
# Build source-specific models
dbt run --select tag:staging

# Build unified model
dbt run --select stg_jobs_unified

# Hoặc build tất cả
dbt run --select models/silver/staging+ stg_jobs_unified
```

### Test

```bash
# Test tất cả
dbt test --select tag:staging stg_jobs_unified

# Test một source cụ thể
dbt test --select stg_joboko_jobs
```

### Run quality checks

```bash
# Compile và xem kết quả
dbt compile --select staging_quality_check

# Copy SQL từ target/compiled/... và run trong database
```

## 📊 Lợi ích

### Trước (Single Model)
```
❌ Một model xử lý tất cả sources
❌ Logic phức tạp, khó maintain
❌ Khó debug khi một source có lỗi
❌ Test chung chung, không specific
```

### Sau (Source-Specific)
```
✅ Mỗi source có logic riêng
✅ Dễ maintain, mỗi file độc lập
✅ Debug dễ dàng, isolate được source
✅ Test chi tiết cho từng source
✅ Performance tốt hơn (parallel runs)
✅ Scalable - thêm source chỉ cần 1 file mới
```

## 🔄 Thêm source mới

1. **Copy template:**
   ```bash
   cp staging/stg_itviec_jobs.sql.template staging/stg_linkedin_jobs.sql
   ```

2. **Customize logic:**
   - Thay `source_site` filter
   - Thay `source_name`
   - Customize salary/experience/education logic

3. **Add to unified:**
   ```sql
   -- Trong stg_jobs_unified.sql
   union all
   select * from {{ ref('stg_linkedin_jobs') }}
   ```

4. **Update schema.yml:**
   ```yaml
   - name: stg_linkedin_jobs
     description: "..."
     tests: [...]
   ```

5. **Test:**
   ```bash
   dbt run --select stg_linkedin_jobs
   dbt test --select stg_linkedin_jobs
   ```

## 📈 Performance Tips

```bash
# Build parallel (3 threads)
dbt run --select tag:staging --threads 3

# Incremental only
dbt run --select tag:staging

# Full refresh khi cần
dbt run --select tag:staging --full-refresh
```

## 🔍 Monitoring

### Check row counts
```sql
select 
  source_name,
  count(*) as jobs,
  max(scraped_date) as latest
from {{ ref('stg_jobs_unified') }}
group by 1;
```

### Check completeness
```sql
select 
  source_name,
  count(*) as total,
  sum(case when salary is null then 1 else 0 end) as missing_salary
from {{ ref('stg_jobs_unified') }}
group by 1;
```

## 📚 Documentation

- `README.md`: Giải thích cấu trúc và quy tắc
- `MIGRATION.md`: Hướng dẫn migration từ model cũ
- `schema.yml`: Tests và column descriptions
- `staging_quality_check.sql`: Quality monitoring queries

## ✅ Checklist triển khai Production

- [x] Tạo source-specific staging models
- [x] Tạo unified model
- [x] Tạo tests
- [x] Tạo macros helper
- [x] Tạo quality check queries
- [x] Tạo documentation
- [ ] Run full refresh test
- [ ] Compare với model cũ (data consistency)
- [ ] Update downstream models (nếu có)
- [ ] Deploy to production
- [ ] Monitor performance
- [ ] Setup alerts cho data quality

## 🎓 Best Practices Applied

1. ✅ **Separation of Concerns**: Mỗi source có logic riêng
2. ✅ **DRY Principle**: Macros cho logic chung
3. ✅ **Incremental Strategy**: Optimize performance
4. ✅ **Testing**: Comprehensive tests
5. ✅ **Documentation**: README, migration guides
6. ✅ **Monitoring**: Quality check queries
7. ✅ **Scalability**: Template cho source mới
8. ✅ **Backward Compatibility**: Giữ model cũ

---

**Created:** October 5, 2025  
**Author:** GitHub Copilot  
**Project:** CrawlJob - Multi-source Job Scraping Pipeline
