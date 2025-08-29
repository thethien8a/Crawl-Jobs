# CrawlJob Frontend Dashboard

Giao diện web dashboard hiện đại cho hệ thống CrawlJob - hiển thị và tìm kiếm dữ liệu việc làm từ nhiều nguồn.

## 📁 Cấu trúc thư mục

```
web/
├── index.html          # Trang chính của dashboard
├── css/
│   ├── styles.css      # CSS chính cho styling
│   └── responsive.css  # CSS responsive cho mobile
├── js/
│   ├── main.js         # Logic chính của ứng dụng
│   ├── api.js          # Xử lý API và network requests
│   └── ui.js           # Helper functions cho UI
└── README.md           # Tài liệu này
```

## 🚀 Cách sử dụng

### 1. Chạy API Backend
```bash
# Từ thư mục gốc project
cd D:\Practice\Scrapy\CrawlJob
python api/main.py
# Hoặc dùng uvicorn
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Mở Frontend
- **Live Server**: Cài extension VS Code → Right-click `index.html` → "Open with Live Server"
- **Local Server**: `python -m http.server 8001` rồi truy cập `http://localhost:8001`
- **Direct**: Mở file trực tiếp (có thể gặp CORS issues)

### 3. Test chức năng
- Nhập từ khóa tìm kiếm (VD: "python", "data analyst")
- Chọn số kết quả/trang
- Click "Tìm kiếm" hoặc nhấn Enter

## ✨ Tính năng

- **🔍 Tìm kiếm thông minh**: Tìm việc theo từ khóa với auto-complete
- **📄 Phân trang**: Navigate qua các trang kết quả mượt mà
- **📊 Thống kê real-time**: Hiển thị số việc làm, nguồn, công ty
- **📱 Responsive**: Tương thích hoàn hảo mobile/desktop
- **🔗 Chi tiết job**: Link trực tiếp đến trang gốc, mô tả đầy đủ
- **🏷️ Nguồn dữ liệu**: Badge màu sắc phân biệt từng website
- **⚡ Performance**: Caching, debouncing, lazy loading
- **🔔 Notifications**: Toast messages cho feedback

## 🏗️ Architecture

### Modular JavaScript Structure

#### `main.js` - Core Application Logic
- Khởi tạo ứng dụng và event listeners
- Quản lý tìm kiếm và phân trang
- State management cho UI

#### `api.js` - API Communication Layer
- HTTP requests với retry logic
- Error handling và timeout
- Response caching
- API configuration

#### `ui.js` - UI Helper Functions
- HTML template generation
- Utility functions (debounce, throttle)
- Animation và transition helpers
- Toast notification system

### CSS Architecture

#### `styles.css` - Main Styles
- Component styling
- Color schemes và themes
- Typography và spacing
- Interactive states

#### `responsive.css` - Responsive Design
- Mobile-first approach
- Breakpoint management
- Adaptive layouts
- Touch-friendly interfaces

## 🎨 Giao diện

- **Bootstrap 5.1.3**: UI framework hiện đại
- **Font Awesome 6.0.0**: Icon library phong phú
- **Google Fonts**: Typography chuyên nghiệp
- **Gradient backgrounds**: Thiết kế thẩm mỹ
- **Card-based layout**: Dễ đọc, hover effects
- **Loading animations**: UX mượt mà
- **Toast notifications**: Feedback tức thời

## 🔧 Cấu hình

### API Configuration
Sửa trong `js/main.js`:
```javascript
const API_BASE = 'http://127.0.0.1:8000';  // Thay đổi endpoint nếu cần
```

### Custom Styling
Sửa trong `css/styles.css`:
```css
:root {
    --primary-color: #667eea;
    --secondary-color: #764ba2;
    --success-color: #28a745;
}
```

## 📱 Screenshots & Demo

Frontend sẽ hiển thị:
- **Header**: Logo và tên project với gradient background
- **Search Box**: Ô tìm kiếm với từ khóa và tùy chọn số kết quả
- **Stats Cards**: Thống kê real-time (số jobs, nguồn, công ty)
- **Job Cards**: Card layout với hover effects, đầy đủ thông tin
- **Pagination**: Điều hướng mượt mà qua các trang
- **Loading States**: Spinner và progress indicators
- **Toast Notifications**: Feedback tức thời cho user actions

## 🔍 API Integration

### Endpoints Used
- `GET /health` - Health check
- `GET /jobs` - Job search với parameters

### Request/Response Format
```javascript
// Request
{
    keyword: "python developer",
    page: 1,
    page_size: 20
}

// Response
{
    items: [
        {
            job_title: "Python Developer",
            company_name: "Tech Corp",
            location: "HCM",
            salary: "20-30 triệu",
            job_url: "https://...",
            source_site: "topcv.vn"
        }
    ],
    total: 150
}
```

## 🐛 Troubleshooting

### CORS Issues
```bash
# Nếu gặp lỗi CORS khi mở trực tiếp HTML
# Giải pháp 1: Live Server extension
# Giải pháp 2: Local server
python -m http.server 8001
# Truy cập: http://localhost:8001
```

### API Connection Issues
```javascript
// Test API connection
fetch('http://127.0.0.1:8000/health')
    .then(r => console.log('API Status:', r.status))
    .catch(e => console.error('Connection Error:', e));
```

### Common Problems
- **"Failed to fetch"**: API server chưa chạy hoặc firewall block
- **"Module not found"**: File paths không chính xác
- **"CORS error"**: Browser security policy, dùng local server
- **"No data"**: Chưa crawl data hoặc database trống

## 🚀 Performance

### Optimizations
- **API Caching**: Cache responses để giảm network requests
- **Debouncing**: Tối ưu search input (300ms delay)
- **Lazy Loading**: Chỉ load dữ liệu khi cần
- **Minification**: Compress CSS/JS cho production

### Bundle Size (approximate)
- `main.js`: ~15KB (gzipped: ~5KB)
- `api.js`: ~12KB (gzipped: ~4KB)
- `ui.js`: ~18KB (gzipped: ~6KB)
- `styles.css`: ~25KB (gzipped: ~8KB)
- **Total**: ~70KB (gzipped: ~22KB)

## 🔮 Future Enhancements

### Planned Features
- [ ] **Advanced Filtering**: Bộ lọc theo lương, địa điểm, kinh nghiệm
- [ ] **Job Bookmarking**: Lưu và quản lý jobs yêu thích
- [ ] **Export Data**: Xuất kết quả ra PDF/Excel
- [ ] **Dark Mode**: Chế độ tối/sáng
- [ ] **Search History**: Lịch sử tìm kiếm
- [ ] **Real-time Updates**: WebSocket notifications

### Technical Improvements
- [ ] **PWA Support**: Progressive Web App
- [ ] **Service Worker**: Offline caching
- [ ] **TypeScript**: Type safety
- [ ] **Testing**: Unit tests cho modules
- [ ] **Build System**: Webpack/Vite bundling

## 📄 License

Part of CrawlJob project. See main project LICENSE file.

---

**Cập nhật lần cuối**: December 2024
**Phiên bản**: 2.0.0 (Modular Architecture)
