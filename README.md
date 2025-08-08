# Job Scraping Project

Dự án web scraping để lấy dữ liệu việc làm từ các trang tuyển dụng Việt Nam như JobsGO và TopCV.

## 🎯 Tính năng

- **Input**: Từ khóa việc làm và địa điểm
- **Output**: Dữ liệu việc làm được lưu vào SQL Server
- **Sites**: JobsGO, TopCV
- **Data**: Job title, company, salary, location, requirements, etc.

## 📋 Cài đặt

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Cấu hình SQL Server

Chỉnh sửa file `CrawlJob/settings.py`:

```python
# SQL Server Database Configuration
SQL_SERVER = "localhost"  # Thay đổi thành SQL Server instance của bạn
SQL_DATABASE = "JobDatabase"  # Thay đổi thành tên database
SQL_USERNAME = "sa"  # Thay đổi thành username
SQL_PASSWORD = "your_password"  # Thay đổi thành password
```

### 3. Tạo database

Tạo database `JobDatabase` trong SQL Server. Spider sẽ tự động tạo bảng `jobs` khi chạy lần đầu.

## 🚀 Sử dụng

### Cách 1: Sử dụng script run_spider.py

```bash
# Chạy spider JobsGO
python run_spider.py --spider jobsgo --keyword "python developer" --location "Hồ Chí Minh"

# Chạy spider TopCV
python run_spider.py --spider topcv --keyword "java developer" --location "Hà Nội"

# Chạy cả hai spider
python run_spider.py --spider both --keyword "data analyst" --location "Đà Nẵng"

# Lưu kết quả vào file JSON
python run_spider.py --spider jobsgo --keyword "marketing" --output "marketing_jobs.json"
```

### Cách 2: Sử dụng Scrapy command

```bash
# Chạy spider JobsGO
scrapy crawl jobsgo -a keyword="python developer" -a location="Hồ Chí Minh"

# Chạy spider TopCV
scrapy crawl topcv -a keyword="java developer" -a location="Hà Nội"
```

## 📊 Cấu trúc dữ liệu

Bảng `jobs` trong SQL Server:

| Field | Type | Description |
|-------|------|-------------|
| id | INT | Primary key |
| job_title | NVARCHAR(500) | Tên công việc |
| company_name | NVARCHAR(500) | Tên công ty |
| salary | NVARCHAR(200) | Mức lương |
| location | NVARCHAR(200) | Địa điểm |
| job_type | NVARCHAR(100) | Loại công việc (Full-time, Part-time) |
| experience_level | NVARCHAR(200) | Yêu cầu kinh nghiệm |
| education_level | NVARCHAR(200) | Yêu cầu học vấn |
| job_description | NVARCHAR(MAX) | Mô tả công việc |
| requirements | NVARCHAR(MAX) | Yêu cầu công việc |
| benefits | NVARCHAR(MAX) | Phúc lợi |
| posted_date | NVARCHAR(200) | Ngày đăng |
| source_site | NVARCHAR(100) | Nguồn dữ liệu |
| job_url | NVARCHAR(1000) | URL công việc |
| search_keyword | NVARCHAR(200) | Từ khóa tìm kiếm |
| scraped_at | NVARCHAR(50) | Thời gian scrape |
| created_at | DATETIME | Thời gian tạo record |

## 🛠️ Cấu trúc project

```
CrawlJob/
├── CrawlJob/
│   ├── spiders/
│   │   ├── jobsgo_spider.py    # Spider cho JobsGO
│   │   └── topcv_spider.py     # Spider cho TopCV
│   ├── items.py                # Định nghĩa cấu trúc dữ liệu
│   ├── pipelines.py            # Pipeline xử lý dữ liệu
│   └── settings.py             # Cấu hình project
├── run_spider.py               # Script chạy spider
├── requirements.txt            # Dependencies
└── README.md                  # Hướng dẫn sử dụng
```

## ⚙️ Cấu hình nâng cao

### Thay đổi delay giữa các request

Chỉnh sửa `DOWNLOAD_DELAY` trong `settings.py`:

```python
DOWNLOAD_DELAY = 2  # Delay 2 giây giữa các request
```

### Thay đổi số lượng request đồng thời

```python
CONCURRENT_REQUESTS = 8  # Số request đồng thời
```

### Thêm User Agent

```python
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
```

## 🔧 Troubleshooting

### Lỗi kết nối SQL Server

1. Kiểm tra SQL Server đang chạy
2. Kiểm tra thông tin đăng nhập trong `settings.py`
3. Đảm bảo database đã được tạo

### Lỗi scraping

1. Kiểm tra internet connection
2. Thử tăng `DOWNLOAD_DELAY`
3. Kiểm tra website có thay đổi cấu trúc HTML không

### Lỗi CSS selector

Các spider sử dụng CSS selector linh hoạt để tìm dữ liệu. Nếu website thay đổi cấu trúc, cần cập nhật selector trong spider.

## 📝 Ghi chú

- Spider tuân thủ robots.txt và có delay giữa các request
- Dữ liệu được lưu vào SQL Server với encoding UTF-8
- Có thể mở rộng thêm các trang tuyển dụng khác
- Spider tự động tạo bảng nếu chưa tồn tại

## 🤝 Đóng góp

Để thêm spider cho trang tuyển dụng mới:

1. Tạo file spider mới trong `spiders/`
2. Kế thừa từ `scrapy.Spider`
3. Implement các method `start_requests()`, `parse_search_results()`, `parse_job_detail()`
4. Thêm spider vào `run_spider.py`

## 📄 License

MIT License
