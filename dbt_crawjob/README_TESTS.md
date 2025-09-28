# DBT Tests Documentation

## Tổng quan

Project này sử dụng dbt tests để kiểm tra chất lượng dữ liệu ở các layer khác nhau:
- **Bronze layer**: Kiểm tra dữ liệu thô từ PostgreSQL
- **Silver layer**: Kiểm tra dữ liệu đã được transform và làm sạch

## Cấu trúc Tests

### Bronze Layer Tests (`tests/bronze_jobs_data_quality.yml`)
- **Not null constraints**: Kiểm tra các trường bắt buộc không được null
- **Unique constraints**: Kiểm tra job_url là duy nhất
- **Data quality**: Kiểm tra độ dài hợp lý của text fields
- **Freshness**: Kiểm tra dữ liệu được crawl trong 7 ngày gần đây
- **Valid source sites**: Kiểm tra source_site có giá trị hợp lệ

### Silver Layer Tests (`tests/silver_jobs_business_rules.yml`)
- **Data normalization**: Kiểm tra job_title, company_name đã được normalize
- **Business rules**: Kiểm tra format salary, deadline hợp lý
- **Data completeness**: Kiểm tra thông tin cơ bản đầy đủ
- **No duplicates**: Kiểm tra không có dữ liệu trùng lặp
- **Incremental load**: Kiểm tra dữ liệu được cập nhật gần đây

## Cách chạy Tests

### 1. Chạy tất cả tests
```bash
cd /d D:\Practice\Scrapy\CrawlJob
dbt test
```

### 2. Chạy tests theo model
```bash
# Test bronze layer
dbt test --model bronze

# Test silver layer
dbt test --model silver
```

### 3. Chạy test cụ thể
```bash
# Test not null constraints
dbt test --select "test_bronze_jobs_job_url_not_null"

# Test business rules
dbt test --select "test_silver_jobs_normalized_job_title"
```

### 4. Chạy tests với profile cụ thể
```bash
dbt test --profile crawljob
```

### 5. Chạy tests với vars (nếu cần)
```bash
dbt test --vars '{"execution_date": "2024-01-01"}'
```

## Kiểm tra kết quả

### Xem kết quả tests
```bash
# Xem chi tiết test results
dbt test --store-failures

# Generate test report
dbt docs generate
dbt docs serve
```

### Debug khi test fail
```bash
# Xem SQL được generate
dbt compile

# Test với dry run
dbt test --select "test_name" --defer
```

## Automation với CI/CD

### Tạo script tự động chạy tests
```bash
#!/bin/bash
cd /d D:\Practice\Scrapy\CrawlJob

# Load environment variables
for /f "tokens=*" %i in (.env) do (
  if not "%i:~0,1%"=="#" (
    if not "%i:~0,1%"==" " (
      if not "%i"=="" set %i
    )
  )
)

# Run tests
dbt test

# Check exit code
if %ERRORLEVEL% NEQ 0 (
  echo "Tests failed!"
  exit 1
) else (
  echo "All tests passed!"
  exit 0
)
```

### PowerShell version
```powershell
# Load .env file
Get-Content .env | ForEach-Object {
    if ($_ -and !$_.StartsWith("#")) {
        $key, $value = $_ -split '=', 2
        if ($key -and $value) {
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
}

# Run tests
dbt test

# Check exit code
if ($LASTEXITCODE -ne 0) {
    Write-Host "Tests failed!" -ForegroundColor Red
    exit 1
} else {
    Write-Host "All tests passed!" -ForegroundColor Green
    exit 0
}
```

## Monitoring và Alerting

### Tích hợp với monitoring tools
```yaml
# Example with DataDog
alerts:
  - name: "dbt_test_failures"
    condition: "dbt test exit code != 0"
    notification_channels: ["slack-data-team"]
```

## Troubleshooting

### Các lỗi thường gặp

1. **"env var required not provided"**
   - Đảm bảo biến môi trường được set
   - Sử dụng script load_env.ps1

2. **"relation does not exist"**
   - Chạy dbt run trước để tạo tables
   - Kiểm tra connection string

3. **"syntax error"**
   - Kiểm tra SQL syntax trong test files
   - Validate với `dbt compile`

### Debug steps
```bash
# 1. Check connection
dbt debug --profile crawljob

# 2. List all tests
dbt list --resource-type test

# 3. Compile tests to SQL
dbt compile

# 4. Run specific test
dbt test --select "test_name"

# 5. Check logs
dbt test --log-level debug
```

## Best Practices

1. **Tên test rõ ràng**: Sử dụng prefix để group tests
2. **Single responsibility**: Mỗi test kiểm tra một rule
3. **Documentation**: Comment rõ ràng trong SQL
4. **Performance**: Optimize queries cho large datasets
5. **Maintenance**: Review và update tests định kỳ

## Schema Validation

Tests tự động validate schema với:
- Data types
- Constraints (not null, unique)
- Accepted values
- Referential integrity

## CI/CD Integration

### GitHub Actions Example
```yaml
name: DBT Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - run: pip install dbt-duckdb
      - run: dbt test