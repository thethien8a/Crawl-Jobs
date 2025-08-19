# LinkedIn Collection Plan (Public Jobs Panel)

> Reference: `https://www.linkedin.com/jobs/search?keywords=Data%20Analyst&location=Vietnam`

## 🎯 Goal
- Thu thập dữ liệu việc làm LinkedIn (public) bằng cách click từng job ở danh sách bên trái để hiển thị panel chi tiết bên phải (không đăng nhập).
- Chuẩn hoá về `JobItem` và ghi qua pipeline SQL Server (dedup theo `(source_site, job_url)`, upsert `updated_at`).

## ✅ Prerequisites
- Thư viện đã có: `selenium`, `webdriver-manager` (trong `requirements.txt`).
- DB/Pipeline hoạt động (đã cấu hình `.env` và chạy được các spider hiện tại).
- Không đăng nhập; tôn trọng TOS. Chỉ lấy nội dung public hiển thị ở panel phải.

## ⚙️ Configuration (đề xuất)
- Tham số hoá (có thể hard-code giai đoạn đầu, nâng cấp sang `.env` sau):
  - `MAX_PAGES = 3..5`
  - `CLICK_DELAY_RANGE = (2, 5)` (giây)
  - `SELENIUM_HEADLESS = True`
  - `WINDOW_SIZE = 1366x900`
  - `WAIT_TIMEOUT = 15` (giây)
- `custom_settings` trong `linkedin_spider.py` (không ảnh hưởng spider khác):
  - `CONCURRENT_REQUESTS = 1`
  - (Tuỳ chọn) bật `CrawlJob.selenium_middleware.SeleniumMiddleware` chỉ cho spider này nếu dùng middleware.

## 📦 JobItem Mapping
- `job_title`: tiêu đề trong panel phải (heading top card).
- `company_name`: link/text gần tiêu đề.
- `salary`: thường không có → để trống nếu không thấy.
- `location`: text gần tên công ty (ví dụ: “Ho Chi Minh City, Vietnam”).
- `job_type`, `experience_level`, `education_level`, `job_industry`, `job_position`: best-effort (có thể trống).
- `job_description`: khối mô tả trong panel phải (mục “Job Description”).
- `requirements`: mục “Requirements” nếu có (fallback: phần mô tả liên quan).
- `benefits`: mục “Benefits” nếu có.
- `job_deadline`: không có → trống.
- `job_url`: lấy từ anchor của item bên trái (ưu tiên) hoặc current URL nếu điều hướng.
- `source_site`: `linkedin.com`.
- `search_keyword`: keyword đầu vào.
- `scraped_at`: ISO timestamp.

## 🧭 Selectors (baseline + fallback)
- Danh sách job (bên trái):
  - CSS: `main ul li a[href*="/jobs/view/"]`
  - CSS bổ sung: `main [data-automation*="job-card" i] a[href*="/jobs/view/"]`
- Panel phải (top card + nội dung):
  - Title (CSS): `main h1, main h2`
  - Company (CSS): `main a[href*="/company/"]`, fallback: heading kế bên title
  - Description (XPaths gợi ý):
    - `//strong[normalize-space()='Job Description']/following-sibling::*[1]//text()`
    - Fallback container CSS: `[data-automation*='jobAdDetails' i] ::text`
  - Requirements/Benefits (XPaths tương tự):
    - `//strong[contains(normalize-space(.), 'Requirements')]/following-sibling::*[1]//text()`
    - `//strong[contains(normalize-space(.), 'Benefits')]/following-sibling::*[1]//text()`
- Pagination (tiếp trang):
  - CSS: `a[rel='next']`, fallback: `a[aria-label*='Next' i]`

## 🔄 Thuật toán (step-by-step)
1) Xây URL tìm kiếm từ `keyword` (và tuỳ chọn `location`), mở bằng Selenium (headless + window size).
2) `WebDriverWait` cho đến khi danh sách hiển thị (ít nhất 1 anchor `/jobs/view/`).
3) Lặp qua item theo index trong trang hiện tại:
   - Scroll item vào viewport (scrollIntoView) → giảm lỗi không thể click.
   - Trích `job_url` từ anchor trước khi click (nếu có).
   - Click item → `WebDriverWait` cho title panel phải đổi (hoặc chờ element mô tả xuất hiện).
   - Nếu có “Show more” trong mô tả → click để mở rộng.
   - Trích xuất các trường theo Mapping (dùng CSS/XPath ở trên).
   - Yield `JobItem` (đầy đủ metadata: `source_site='linkedin.com'`, `search_keyword`, `scraped_at`).
   - `time.sleep(random.uniform(*CLICK_DELAY_RANGE))` giữa các click.
4) Phân trang: tìm `Next` → click → lặp lại đến `MAX_PAGES` hoặc hết trang.
5) Bắt lỗi từng item (try/except), log cảnh báo, tiếp tục vòng lặp.

## 🛡️ Chống bot & Độ bền
- Delay ngẫu nhiên 2–5s mỗi click; có thể tăng nếu nghi ngờ throttling.
- Headless + viewport lớn; cuộn tự nhiên để kích hoạt lazy-load.
- UA đã set trong `settings.py`; cân nhắc xoay UA nếu bị block.
- Nếu gặp captcha/block: dừng sớm trang hiện tại, giảm tốc, thử lại (không vượt cơ chế bảo vệ).
- Đóng gói selector qua helper để dễ bảo trì khi UI đổi.

## 🔌 Tích hợp với dự án
- Tạo `CrawlJob/spiders/linkedin_spider.py` (Selenium-driven):
  - Thuộc tính: `name='linkedin'`, nhận `keyword`, optional `location`.
  - `custom_settings`: hạn chế concurrency, bật middleware nếu dùng.
- Cập nhật `run_spider.py`:
  - Import `LinkedinSpider`, thêm vào `--spider linkedin` và `all`.
- Cập nhật `README.md`:
  - Hướng dẫn chạy: `python run_spider.py --spider linkedin --keyword "Data Analyst"`.
  - Lưu ý: site động, plan best-effort; có thể thay đổi UI theo thời gian.
- Không đổi `pipelines.py`: logic dedup/upsert đã phù hợp.

## 🧪 Test & Validation
- Smoke test: chạy với `--keyword "Data Analyst"` → xác minh có item vào DB và JSON.
- Re-run cùng keyword: không trùng dữ liệu (nhờ unique `(source_site, job_url)`), `updated_at` thay đổi.
- Spot-check 10 job: có đủ title/company/location/description; mô tả mở rộng khi click “Show more”.
- Theo dõi log: không lỗi nghiêm trọng; crawl xong trong thời gian hợp lý.

## 🎯 Acceptance Criteria (DoD)
- ≥ 50 job cho 1 keyword phổ biến (tuỳ thời điểm hiển thị của LinkedIn).
- ≥ 80% item có: `job_title`, `company_name`, `location`, `job_description`.
- Rerun không tạo bản ghi trùng; `updated_at` cập nhật khi nội dung thay đổi.
- Selector/logic tách riêng, dễ chỉnh khi UI đổi; log rõ ràng cho lỗi/skip.

## ⏱️ Timeline (ước lượng)
- Spider (Selenium) + wiring runner: 1.5–2 giờ
- Tối ưu selector/chống bot + README: 45–60 phút
- Tinh chỉnh theo UI thay đổi: lặp nhỏ khi cần

## 📦 Deliverables
- `CrawlJob/spiders/linkedin_spider.py` (Selenium click-through panel phải)
- `run_spider.py` (thêm `linkedin` vào lựa chọn và `all`)
- README: mục hướng dẫn LinkedIn (ghi chú site động, best-effort)

## ⚖️ Legal & TOS
- Chỉ thu thập nội dung public; tôn trọng TOS và robots của LinkedIn.
- Không cố vượt captcha/chặn; giảm tần suất hoặc dừng khi phát hiện hạn chế.
