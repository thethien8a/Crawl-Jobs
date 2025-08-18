# Job Scraping Project

Dự án web scraping để lấy dữ liệu việc làm từ các trang tuyển dụng Việt Nam như JobsGO, JobOKO, 123job, CareerViet và JobStreet.

## 🎯 Tính năng

- **Input**: Từ khóa việc làm
- **Output**: Dữ liệu việc làm được lưu vào SQL Server
- **Sites**: JobsGO, JobOKO, 123job, CareerViet, JobStreet
- **Data**: Job title, company, salary, location, requirements, job_deadline, etc.

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

Hoặc tạo file `.env` ở thư mục gốc (khuyến nghị an toàn):

```env
SQL_SERVER=localhost
SQL_DATABASE=JobDatabase
SQL_USERNAME=sa
SQL_PASSWORD=your_password
```

Ghi chú: `settings.py` đã tự động đọc biến môi trường (qua `python-dotenv`) nếu có file `.env`.

### 3. Tạo database

Tạo database `JobDatabase` trong SQL Server. Pipeline sẽ **tạo bảng `jobs` nếu chưa tồn tại** khi chạy lần đầu.

## 🚀 Sử dụng

### Cách 1: Sử dụng script run_spider.py

```bash
# Chạy spider JobsGO
python run_spider.py --spider jobsgo --keyword "python developer"

# Chạy spider JobOKO
python run_spider.py --spider joboko --keyword "java developer"

# Chạy spider 123job
python run_spider.py --spider 123job --keyword "data analyst"

# Chạy spider CareerViet
python run_spider.py --spider careerviet --keyword "data analyst"

# Chạy spider JobStreet
python run_spider.py --spider jobstreet --keyword "data analyst"

# Chạy tất cả spider
python run_spider.py --spider all --keyword "developer"

# Lưu kết quả vào file JSON
python run_spider.py --spider jobsgo --keyword "marketing" --output "marketing_jobs.json"
```

### API Read-Only (FastAPI)

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload

# Kiểm tra
curl http://127.0.0.1:8000/health
curl "http://127.0.0.1:8000/jobs?keyword=python&site=jobsgo&page=1&page_size=20"
```

### Cách 2: Sử dụng Scrapy command

```bash
# Chạy spider JobsGO
scrapy crawl jobsgo -a keyword="python developer"

# Chạy spider JobOKO
scrapy crawl joboko -a keyword="java developer"

# Chạy spider 123job
scrapy crawl 123job -a keyword="data analyst"

# Chạy spider CareerViet
scrapy crawl careerviet -a keyword="data analyst"

# Chạy spider JobStreet
scrapy crawl jobstreet -a keyword="data analyst"
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
| job_industry | NVARCHAR(200) | Ngành nghề |
| job_position | NVARCHAR(200) | Chức vụ/Vị trí |
| job_description | NVARCHAR(MAX) | Mô tả công việc |
| requirements | NVARCHAR(MAX) | Yêu cầu công việc |
| benefits | NVARCHAR(MAX) | Phúc lợi |
| job_deadline | NVARCHAR(200) | Hạn cuối nộp CV |
| source_site | NVARCHAR(100) | Nguồn dữ liệu |
| job_url | NVARCHAR(1000) | URL công việc |
| search_keyword | NVARCHAR(200) | Từ khóa tìm kiếm |
| scraped_at | NVARCHAR(50) | Thời gian scrape |
| created_at | DATETIME | Thời gian tạo record |

Lưu ý: Nếu bảng `jobs` đã tồn tại trước khi thêm cột mới (ví dụ `job_position`) thì cần ALTER thủ công:

```sql
IF COL_LENGTH('dbo.jobs','job_position') IS NULL
    ALTER TABLE dbo.jobs ADD job_position NVARCHAR(200) NULL;
```

## 🛠️ Cấu trúc project

```
CrawlJob/
├── CrawlJob/
│   ├── spiders/
│   │   ├── jobsgo_spider.py     # Spider cho JobsGO
│   │   ├── joboko_spider.py     # Spider cho JobOKO
│   │   ├── job123_spider.py     # Spider cho 123job
│   │   └── careerviet_spider.py # Spider cho CareerViet
│   ├── items.py                 # Định nghĩa cấu trúc dữ liệu
│   ├── pipelines.py             # Pipeline xử lý dữ liệu (SQL Server, dedup/upsert)
│   ├── settings.py              # Cấu hình project
│   ├── selenium_middleware.py   # (Tùy chọn) Middleware Selenium - hiện đang tắt
│   └── utils.py                 # Tiện ích hỗ trợ (encode_input, encode_joboko_input)
├── api/main.py                  # FastAPI read-only (/health, /jobs)
├── run_spider.py                # Script chạy spider
├── requirements.txt             # Dependencies
├── scrapy.cfg                   # Cấu hình Scrapy
├── crawl_daily.bat              # Script batch chạy định kỳ (logs/outputs có timestamp)
└── README.md                    # Hướng dẫn sử dụng
```

## ⚙️ Cấu hình nâng cao

### Thay đổi delay giữa các request

Chỉnh sửa `DOWNLOAD_DELAY` trong `settings.py`:

```python
DOWNLOAD_DELAY = 2  # Delay 2 giây giữa các request
```

### Thay đổi số lượng request đồng thời

```python
CONCURRENT_REQUESTS = 16  # Số request đồng thời
```

### Thêm User Agent

```python
USER_AGENT = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36"
```

## 🗓️ Scheduling (Windows Task Scheduler)

1. Test thủ công file batch:
```bat
cd /d D:\Practice\Scrapy\CrawlJob
crawl_daily.bat
```
- Kết quả: tạo `outputs\jobs_YYYY-MM-DD_HH-mm-ss.json` và `logs\crawl_YYYY-MM-DD_HH-mm-ss.log`.

2. Tạo task tự động (GUI):
- Task Scheduler → Create Task…
- General: Run whether user is logged on or not; Run with highest privileges
- Triggers: Daily 02:00
- Actions:
  - Program/script: `cmd.exe`
  - Add arguments: `/c D:\Practice\Scrapy\CrawlJob\crawl_daily.bat`
  - Start in: `D:\Practice\Scrapy\CrawlJob`
- Nhấn Run để test

3. Tạo task bằng lệnh (tùy chọn):
```bat
SCHTASKS /Create /TN "CrawlJob Daily" /TR "cmd.exe /c Path_to\crawl_daily.bat" /SC DAILY /ST 02:00 /RL HIGHEST /F
```

4. Lưu ý:
- Nếu `python` không nhận diện, dùng full path tới `python.exe` trong `crawl_daily.bat`.
- Nếu dùng venv, bỏ comment dòng `call ...activate.bat` trong batch.
- Đảm bảo SQL Server bật TCP/IP và cổng đúng (thường 1433), `.env` trỏ đúng `SQL_SERVER`.

### Chi tiết cấu hình Task Scheduler (GUI)

1) Mở Task Scheduler → Create Task… (không phải Basic Task)
- Tab General:
  - Name: CrawlJob Daily (hoặc tên bạn muốn)
  - Description: Chạy `crawl_daily.bat` để thu thập dữ liệu hằng ngày
  - Chọn "Run whether user is logged on or not"
  - Tick "Run with highest privileges"
  - Configure for: Windows 10/11
- Tab Triggers → New…
  - Begin the task: On a schedule
  - Daily, Start at: 02:00 (ví dụ)
  - (Tuỳ chọn) Advanced: Repeat task every: 4 hours; For a duration of: Indefinitely → dùng khi muốn chạy nhiều lần/ngày
  - OK
- Tab Actions → New…
  - Action: Start a program
  - Program/script: `cmd.exe`
  - Add arguments: `/c "D:\Practice\Scrapy\CrawlJob\crawl_daily.bat"`
  - Start in (optional): `D:\Practice\Scrapy\CrawlJob`
  - Lưu ý: luôn bọc đường dẫn có dấu cách trong dấu nháy kép ""
  - OK
- Tab Conditions: tuỳ nhu cầu (ví dụ bỏ chọn "Start the task only if the computer is on AC power")
- Tab Settings:
  - Cho phép "Allow task to be run on demand"
  - Nếu task có thể chạy lâu: điều chỉnh "Stop the task if it runs longer than"
- Nhấn OK và nhập mật khẩu user nếu được yêu cầu

2) Chạy test ngay
- Trong Task Scheduler, chọn task → Run
- Kiểm tra:
  - File `outputs\jobs_*.json` được sinh
  - File `logs\crawl_*.log` có nội dung log

3) Tạo task bằng dòng lệnh (tùy chọn)
```bat
REM Đường dẫn generic (sửa Path_to cho phù hợp)
SCHTASKS /Create /TN "CrawlJob Daily" /TR "cmd.exe /c \"Path_to\\crawl_daily.bat\"" /SC DAILY /ST 02:00 /RL HIGHEST /F

REM Ví dụ theo project này
SCHTASKS /Create /TN "CrawlJob Daily" /TR "cmd.exe /c \"D:\\Practice\\Scrapy\\CrawlJob\\crawl_daily.bat\"" /SC DAILY /ST 02:00 /RL HIGHEST /F

REM Chạy mỗi 4 giờ (lặp vô hạn) bắt đầu từ 00:00
SCHTASKS /Create /TN "CrawlJob Every4H" /TR "cmd.exe /c \"D:\\Practice\\Scrapy\\CrawlJob\\crawl_daily.bat\"" /SC HOURLY /MO 4 /ST 00:00 /RL HIGHEST /F

REM Chạy dưới tài khoản SYSTEM (không cần đăng nhập)
SCHTASKS /Create /TN "CrawlJob SYSTEM" /TR "cmd.exe /c \"D:\\Practice\\Scrapy\\CrawlJob\\crawl_daily.bat\"" /SC DAILY /ST 02:00 /RU SYSTEM /RL HIGHEST /F
```

4) Gợi ý cấu hình trong `crawl_daily.bat`
- Nếu dùng virtualenv, bỏ comment dòng `call ...activate.bat` và sửa path cho đúng
- Nếu `python` không có trong PATH của dịch vụ, dùng full path tới `python.exe` (đã có dòng mẫu trong file .bat)
- Có thể đổi `--keyword` theo nhu cầu

5) Troubleshooting Task Scheduler
- "The system cannot find the file specified": kiểm tra quotes và đường dẫn trong Program/script, Arguments, Start in
- Exit code 1/2: xem file log trong `logs\crawl_*.log` để biết lỗi chi tiết (selector, SQL, mạng…)
- Không tạo ra output/log: kiểm tra quyền ghi thư mục hoặc dùng Start in để đặt Working Directory đúng
- Không kết nối được SQL Server: kiểm tra TCP/IP, port 1433, firewall; `.env` đúng `SQL_SERVER`

## 🔧 Troubleshooting

### Lỗi kết nối SQL Server
1. Kiểm tra SQL Server đang chạy
2. Kiểm tra `.env`: `SQL_SERVER=localhost,1433` hoặc `localhost\SQLEXPRESS`
3. Bật TCP/IP và mở firewall port 1433

### Lỗi scraping
1. Kiểm tra internet connection
2. Thử tăng `DOWNLOAD_DELAY`
3. Kiểm tra website có thay đổi cấu trúc HTML không

### Lỗi CSS selector
- Cập nhật selector trong spider nếu website đổi HTML.

## 📝 Ghi chú

- Spider có delay giữa các request để tránh quá tải server
- Dữ liệu lưu vào SQL Server (UTF-8); dedup theo `(source_site, job_url)` và upsert `updated_at`
- Có thể mở rộng thêm các trang tuyển dụng khác

## 📄 License

MIT License
