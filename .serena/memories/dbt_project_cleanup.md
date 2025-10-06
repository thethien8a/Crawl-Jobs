# CrawlJob - dbt Project Cleanup (Oct 2025)

## Files đã xóa (cleanup)

### 1. Schema files cũ
- ❌ `models/silver/schema.yml` - DELETED
  - Lý do: File này define tests cho model `stg_jobs` không còn tồn tại
  - Đã được thay thế bởi: `models/silver/staging/schema.yml`

### 2. Gitkeep files không cần thiết
- ❌ `analyses/.gitkeep` - DELETED (đã có staging_quality_check.sql)
- ❌ `macros/.gitkeep` - DELETED (đã có 9 macro files)
- ❌ `tests/.gitkeep` - DELETED (đã có test files)

### 3. Gitkeep files giữ lại
- ✅ `seeds/.gitkeep` - GIỮ LẠI (folder chưa có seeds, cần để Git track empty folder)
- ✅ `snapshots/.gitkeep` - GIỮ LẠI (folder chưa có snapshots, cần để Git track empty folder)

## Cấu trúc folder sau cleanup

```
dbt_crawjob/
├── analyses/
│   └── staging_quality_check.sql
├── logs/
│   └── dbt.log
├── macros/
│   ├── normalize_job_fields.sql (NEW)
│   ├── test_deadline_after_scraped.sql
│   ├── test_is_positive.sql
│   ├── test_is_recent.sql
│   ├── test_row_count_in_range.sql
│   ├── test_salary_has_currency.sql
│   ├── test_unique_combination.sql
│   ├── test_valid_source_site.sql
│   └── test_valid_url.sql
├── models/
│   ├── sources.yml
│   ├── gold/
│   └── silver/
│       ├── stg_jobs_unified.sql (NEW)
│       └── staging/
│           ├── IMPLEMENTATION_SUMMARY.md (NEW)
│           ├── MIGRATION.md (NEW)
│           ├── README.md (NEW)
│           ├── schema.yml (NEW - main schema)
│           ├── stg_itviec_jobs.sql.template (NEW)
│           ├── stg_joboko_jobs.sql (NEW)
│           ├── stg_topcv_jobs.sql (NEW)
│           └── stg_vietnamworks_jobs.sql (NEW)
├── seeds/
│   └── .gitkeep (KEPT)
├── snapshots/
│   └── .gitkeep (KEPT)
├── target/
│   └── [compiled files]
├── tests/
│   ├── exist_today.sql
│   └── schema.yml
├── .gitignore
├── .user.yml
├── dbt_project.yml
├── profiles.yml
└── README_TESTS.md
```

## Lý do cleanup

1. **Loại bỏ schema.yml cũ**: 
   - File define tests cho model `stg_jobs` không tồn tại
   - Gây confusion và có thể gây lỗi khi run dbt test
   - Schema mới đã được tổ chức tốt hơn trong `staging/schema.yml`

2. **Loại bỏ .gitkeep không cần**:
   - Folders đã có files thực, không cần .gitkeep để Git tracking
   - Giảm clutter trong project

3. **Giữ lại .gitkeep cho empty folders**:
   - `seeds/` và `snapshots/` chưa có nội dung
   - Cần .gitkeep để Git track structure

## Lợi ích sau cleanup

✅ **Cleaner structure**: Không có files thừa gây confusion  
✅ **Avoid test errors**: Không còn tests cho models không tồn tại  
✅ **Better organization**: Schema được tổ chức rõ ràng theo staging models  
✅ **Easier maintenance**: Ít files hơn, dễ navigate hơn

## Next steps

- [ ] Run `dbt clean` để xóa target/ cache (optional)
- [ ] Run `dbt compile` để verify không có lỗi
- [ ] Run `dbt test --select tag:staging` để test staging models
- [ ] Commit changes to Git
