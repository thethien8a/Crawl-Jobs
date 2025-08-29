# Job Scraping Project

Dự án web scraping để lấy dữ liệu việc làm từ **10 trang tuyển dụng Việt Nam** với kiến trúc **modular** và **production-ready**.

## 🎯 Tính năng

- **Input**: Từ khóa việc làm (VD: "Python Developer", "Data Analyst")
- **Output**: Dữ liệu việc làm được lưu vào SQL Server với deduplication
- **Sites**: JobsGO, JobOKO, 123job, CareerViet, JobStreet, LinkedIn (public), TopCV, ITviec, CareerLink, VietnamWorks
- **Data**: Job title, company, salary, location, requirements, job_deadline, benefits, etc.
- **API**: FastAPI REST endpoints với pagination và search
- **Web Dashboard**: Bootstrap UI với search và pagination
- **Automation**: Windows Task Scheduler cho daily crawling

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

### Sử dụng script run_spider.py

```bash
# Chạy spider JobsGO
python run_spider.py --spider jobsgo --keyword "Data Analyst" --output jobsgo.json

# Chạy spider JobOKO
python run_spider.py --spider joboko --keyword "Data Analyst" --output joboko.json

# Chạy spider 123Job
python run_spider.py --spider job123 --keyword "Data Analyst" --output job123.json

# Chạy spider CareerViet
python run_spider.py --spider careerviet --keyword "Data Analyst" --output careerviet.json

# Chạy spider JobStreet
python run_spider.py --spider jobstreet --keyword "Data Analyst" --output jobstreet.json

# Chạy spider LinkedIn (public): click list → đọc panel phải
python run_spider.py --spider linkedin --keyword "Data Analyst" --output linkedin.json

# Chạy spider TopCV
python run_spider.py --spider topcv --keyword "Data Analyst" --output topcv.json

# Chạy spider ITviec
python run_spider.py --spider itviec --keyword "Data Analyst" --output itviec.json

# Chạy spider CareerLink
python run_spider.py --spider careerlink --keyword "Data Analyst" --output careerlink.json

# Chạy spider VietnamWorks
python run_spider.py --spider vietnamworks --keyword "Data Analyst" --output vietnamworks.json

# Chạy tất cả spider
python run_spider.py --spider all --keyword "Data Analyst" --output all_jobs.json
```

Ghi chú: LinkedIn là site động; spider dùng Selenium click từng job ở danh sách để hiển thị panel phải và trích xuất mô tả/chi tiết cơ bản (không đăng nhập). UI có thể thay đổi theo thời gian, cần điều chỉnh selector khi cần.

### API Read-Only (FastAPI)

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload

# Kiểm tra
curl http://127.0.0.1:8000/health
curl "http://127.0.0.1:8000/jobs?keyword=python&site=jobsgo&page=1&page_size=20"
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
├── 📁 CrawlJob/                 # Main Scrapy project
│   ├── 📁 spiders/              # 10 Job site spiders
│   │   ├── jobsgo_spider.py     # JobsGO.vn (Simple Scrapy)
│   │   ├── joboko_spider.py     # JobOKO.vn (Simple Scrapy)
│   │   ├── job123_spider.py     # 123job.vn (Simple Scrapy)
│   │   ├── careerviet_spider.py # CareerViet.vn (Simple Scrapy)
│   │   ├── jobstreet_spider.py  # JobStreet.vn (Simple Scrapy)
│   │   ├── careerlink_spider.py # CareerLink.vn (Simple Scrapy)
│   │   ├── topcv_spider.py      # TopCV.vn (Enhanced Scrapy + JS extraction)
│   │   ├── vietnamworks_spider.py # VietnamWorks.com (Hybrid Selenium + Scrapy)
│   │   ├── linkedin_spider.py   # LinkedIn.com (Selenium + authentication ready)
│   │   └── itviec_spider.py     # ITviec.com (Selenium + click navigation)
│   ├── items.py                 # JobItem data model (18+ fields)
│   ├── pipelines.py             # SQL Server pipeline với deduplication
│   ├── settings.py              # Scrapy configuration & database settings
│   ├── selenium_middleware.py   # Selenium integration middleware
│   └── utils.py                 # Helper functions (encode_input, clean_location)
├── 📁 api/                      # FastAPI backend
│   └── main.py                  # REST API endpoints (/health, /jobs)
├── 📁 debug/                    # Debug utilities (NEW)
│   └── HTML_export_debug.py     # HTML export tool cho selector testing
├── 📁 web/                      # Web dashboard (Modular Architecture)
│   ├── index.html               # Trang chính của dashboard
│   ├── css/                     # Stylesheets
│   │   ├── styles.css          # CSS chính
│   │   └── responsive.css      # Responsive design
│   ├── js/                     # JavaScript modules
│   │   ├── main.js            # Logic chính của ứng dụng
│   │   ├── api.js             # API communication layer
│   │   └── ui.js              # UI helper functions
│   └── README.md               # Comprehensive documentation
├── 📁 logs/                     # Crawling logs (timestamped)
├── 📁 outputs/                  # JSON output files (timestamped)
├── 📄 run_spider.py             # CLI runner cho tất cả spiders
├── 📄 requirements.txt          # Python dependencies (11 packages)
├── 📄 scrapy.cfg                # Scrapy project configuration
├── 📄 crawl_daily.bat           # Windows Task Scheduler automation
├── 📄 env.example               # Environment variables template
├── 📄 test.ipynb                # Jupyter notebook cho testing
├── 📄 vietnamworks.json         # VietnamWorks output sample
└── 📄 README.md                 # Hướng dẫn sử dụng
```

### 🆕 **Spider Categories**
- **Simple Scrapy** (6 sites): JobsGO, JobOKO, 123job, CareerViet, JobStreet, CareerLink
- **Enhanced Scrapy** (2 sites): TopCV (JavaScript extraction), ITviec (Advanced selectors)
- **Hybrid Selenium + Scrapy** (1 site): VietnamWorks (Selenium URL collection + Scrapy parsing)
- **Selenium-Based** (1 site): LinkedIn (Browser automation)

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

## 🐛 Debug & Testing Tools

### HTML Export Tool
Script `debug/HTML_export_debug.py` để export HTML từ job sites cho việc testing selectors:

```bash
cd debug
python HTML_export_debug.py
```

### Jupyter Notebook Testing
File `test.ipynb` cho testing và development:

```bash
jupyter notebook test.ipynb
```

### Sample Output Files
- `vietnamworks.json` - Sample output từ VietnamWorks spider
- `outputs/jobs_*.json` - Timestamped output files
- `logs/crawl_*.log` - Timestamped log files

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
4. Kiểm tra database permissions cho user

### Lỗi scraping
1. Kiểm tra internet connection
2. Thử tăng `DOWNLOAD_DELAY` trong `settings.py`
3. Kiểm tra website có thay đổi cấu trúc HTML không
4. Sử dụng debug tools để export HTML: `python debug/HTML_export_debug.py`

### Lỗi CSS selector
- Cập nhật selector trong spider nếu website đổi HTML
- Sử dụng `debug/HTML_export_debug.py` để test selectors
- Check `logs/crawl_*.log` cho error messages

### Spider-Specific Issues

#### Selenium Spiders (LinkedIn, ITviec)
- **ChromeDriver issues**: Cài đặt `webdriver-manager` hoặc update Chrome
- **Anti-detection**: Spiders có anti-detection measures built-in
- **Login required**: Một số sites yêu cầu authentication (ITviec)
- **Slow performance**: Selenium spiders chậm hơn Scrapy spiders

#### JavaScript-Heavy Sites (TopCV)
- **Dynamic content**: Sử dụng enhanced parsing với JavaScript extraction
- **Missing data**: Một số fields có thể missing do dynamic loading
- **Rate limiting**: TopCV có strict rate limiting

#### Advanced Scrapy (VietnamWorks)
- **Complex selectors**: Sử dụng multiple fallback selectors
- **Pagination**: Limited to 5 pages để tránh blocking
- **Data quality**: High quality data với comprehensive fields

### Debug Tools Usage
```bash
# Export HTML để debug selectors
cd debug
python HTML_export_debug.py

# Check logs cho errors
type logs\crawl_*.log

# Test individual spider
python run_spider.py --spider topcv --keyword "python" --output debug.json
```

### Performance Optimization
1. **Rate Limiting**: Adjust `DOWNLOAD_DELAY` based on site restrictions
2. **Concurrent Requests**: Reduce `CONCURRENT_REQUESTS` nếu bị block
3. **Memory Usage**: Monitor RAM usage với large datasets
4. **Database Performance**: Ensure SQL Server có đủ resources

## 📝 Ghi chú

- **10 Job Sites**: Coverage toàn diện các trang tuyển dụng lớn tại Việt Nam
- **Smart Deduplication**: Loại bỏ duplicate dựa trên `(job_title, company_name, source_site)`
- **Rate Limiting**: Respectful crawling với 2s delay giữa requests
- **Error Resilience**: Graceful handling cho individual spider failures
- **Production Ready**: Windows Task Scheduler integration
- **Modular Architecture**: Dễ dàng thêm job sites mới
- **Debug Tools**: Built-in tools cho testing và troubleshooting
- **Data Quality**: Comprehensive 18+ field data model

### 🆕 **Recent Updates**
- **New Spiders**: ITviec (Selenium), VietnamWorks (Advanced Scrapy)
- **Debug Tools**: HTML export utility cho selector testing
- **Enhanced Documentation**: Detailed troubleshooting guides
- **Performance Optimization**: Better memory management và error handling

### 🚀 **Future Enhancements**
- **ML Integration**: Job matching algorithms
- **Real-time Notifications**: Push notifications cho new jobs
- **Advanced Analytics**: Salary analysis và trend detection
- **API Rate Limiting**: Production-ready API management

## 📄 License

MIT License
