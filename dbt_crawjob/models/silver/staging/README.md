# Staging Layer - Source-Specific Models

Folder này chứa các staging models cho từng source site riêng biệt.

## Cấu trúc

```
staging/
├── stg_joboko_jobs.sql       # Logic riêng cho JobOKO
├── stg_topcv_jobs.sql         # Logic riêng cho TopCV
├── stg_vietnamworks_jobs.sql  # Logic riêng cho VietnamWorks
└── schema.yml                 # Tests và documentation
```

## Quy trình data flow

```
bronze.jobs (raw)
    ↓
    ├─→ stg_joboko_jobs.sql      (JobOKO-specific cleaning)
    ├─→ stg_topcv_jobs.sql       (TopCV-specific cleaning)
    └─→ stg_vietnamworks_jobs.sql (VietnamWorks-specific cleaning)
         ↓
    stg_jobs_unified.sql (Union tất cả)
         ↓
    Gold layer models
```

## Tại sao tách riêng theo source?

1. **Mỗi site có format khác nhau**:
   - JobOKO: "Thỏa thuận", "10-15 triệu"
   - TopCV: "Up to 2000 USD", có logic riêng cho brand URLs
   - VietnamWorks: "You'll love it", "$2000"

2. **Dễ maintain**: Khi một site thay đổi format, chỉ cần sửa 1 file

3. **Testing tốt hơn**: Test riêng từng source với logic phù hợp

4. **Performance**: Có thể optimize incremental strategy cho từng source

## Cách thêm source mới

1. Tạo file mới: `stg_<source_name>_jobs.sql`
2. Copy template từ một file có sẵn
3. Customize logic cleaning cho source đó
4. Thêm vào `stg_jobs_unified.sql` (UNION ALL)
5. Update `schema.yml` với tests phù hợp

## Quy tắc chung

- Unique key: `job_url`
- Incremental strategy: `merge`
- Schema: `silver`
- Tất cả đều có `source_name` column để dễ tracking
