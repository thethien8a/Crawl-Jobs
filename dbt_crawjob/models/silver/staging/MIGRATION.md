# Migration Guide: Từ stg_jobs sang Source-Specific Models

## Tổng quan thay đổi

### Trước (Single Staging Model):
```
bronze.jobs → stg_jobs.sql → Gold layer
```

### Sau (Source-Specific Models):
```
bronze.jobs 
    ↓
    ├─→ stg_joboko_jobs.sql
    ├─→ stg_topcv_jobs.sql  
    └─→ stg_vietnamworks_jobs.sql
         ↓
    stg_jobs_unified.sql → Gold layer
```

## Các bước migration

### Bước 1: Kiểm tra model hiện tại
```bash
# Xem model cũ đang chạy
dbt run --select stg_jobs

# Xem lineage
dbt ls --select stg_jobs+
```

### Bước 2: Build staging models mới
```bash
# Build từng model riêng lẻ
dbt run --select stg_joboko_jobs
dbt run --select stg_topcv_jobs
dbt run --select stg_vietnamworks_jobs

# Hoặc build tất cả staging models
dbt run --select tag:staging
```

### Bước 3: Build unified model
```bash
dbt run --select stg_jobs_unified
```

### Bước 4: Test models mới
```bash
# Test tất cả staging models
dbt test --select tag:staging

# Test unified model
dbt test --select stg_jobs_unified
```

### Bước 5: Update downstream models

Nếu có models khác đang dùng `stg_jobs`, cần update:

**Trước:**
```sql
select * from {{ ref('stg_jobs') }}
```

**Sau:**
```sql
select * from {{ ref('stg_jobs_unified') }}
```

### Bước 6: Verify data consistency

```sql
-- So sánh số lượng records
select 
  'old_model' as source,
  count(*) as row_count
from {{ ref('stg_jobs') }}

union all

select 
  'new_model' as source,
  count(*) as row_count  
from {{ ref('stg_jobs_unified') }}
```

## Lợi ích của approach mới

### 1. Maintainability
- ✅ Mỗi source có logic riêng, dễ debug
- ✅ Thay đổi một source không ảnh hưởng source khác

### 2. Performance  
- ✅ Incremental strategy tối ưu cho từng source
- ✅ Có thể chạy parallel các staging models

### 3. Testing
- ✅ Test riêng từng source với logic phù hợp
- ✅ Dễ phát hiện lỗi từ source cụ thể

### 4. Scalability
- ✅ Thêm source mới chỉ cần tạo 1 file
- ✅ Không cần modify model chung

## Commands hữu ích

```bash
# Build tất cả staging models song song
dbt run --select tag:staging --threads 3

# Build chỉ JobOKO staging
dbt run --select stg_joboko_jobs

# Test một source cụ thể
dbt test --select stg_topcv_jobs

# Build từ staging → unified → gold
dbt run --select tag:staging stg_jobs_unified tag:gold

# Xem compiled SQL của một model
dbt compile --select stg_joboko_jobs
# File sẽ ở: target/compiled/...

# Debug một model
dbt run --select stg_joboko_jobs --debug
```

## Rollback plan

Nếu cần quay lại model cũ:

1. Giữ nguyên file `stg_jobs.sql`
2. Update downstream models về dùng `stg_jobs`
3. Drop các staging models mới (optional)

```bash
# Drop staging tables (nếu cần)
dbt run-operation drop_model --args '{model_name: stg_joboko_jobs}'
```

## Checklist

- [ ] Build tất cả source-specific staging models
- [ ] Build unified model
- [ ] Run tests và pass
- [ ] Update downstream models (nếu có)
- [ ] Verify data consistency
- [ ] Update documentation
- [ ] Deploy to production

## Best Practices

1. **Incremental runs**: Always test full refresh first
   ```bash
   dbt run --select stg_joboko_jobs --full-refresh
   ```

2. **Data quality**: Monitor row counts per source
   ```sql
   select 
     source_name,
     count(*) as jobs,
     max(scraped_at) as latest_scrape
   from {{ ref('stg_jobs_unified') }}
   group by 1
   ```

3. **Documentation**: Keep README updated khi thêm source mới
