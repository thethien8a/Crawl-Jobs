# CrawlJob Frontend

Frontend web đơn giản để test API CrawlJob.

## 🚀 Cách sử dụng

### 1. Chạy API Backend
```bash
# Từ thư mục gốc project
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Mở Frontend
- Mở file `web/index.html` trực tiếp trong trình duyệt
- Hoặc dùng Live Server (VS Code extension) để chạy local server

### 3. Test chức năng
- Nhập từ khóa tìm kiếm (VD: "python", "data analyst")
- Chọn số kết quả/trang
- Click "Tìm kiếm"

## ✨ Tính năng

- **Tìm kiếm**: Tìm việc theo từ khóa
- **Phân trang**: Navigate qua các trang kết quả
- **Thống kê**: Hiển thị số việc làm, nguồn, công ty
- **Responsive**: Tương thích mobile/desktop
- **Chi tiết job**: Link đến trang gốc, mô tả đầy đủ
- **Nguồn dữ liệu**: Badge màu sắc cho từng site

## 🎨 Giao diện

- **Bootstrap 5**: UI framework hiện đại
- **Font Awesome**: Icons đẹp
- **Gradient background**: Thiết kế chuyên nghiệp
- **Card layout**: Dễ đọc, hover effects
- **Loading states**: UX tốt khi chờ API

## 🔧 Cấu hình

Nếu API chạy ở port khác, sửa trong `index.html`:
```javascript
const API_BASE = 'http://127.0.0.1:YOUR_PORT';
```

## 📱 Screenshots

Frontend sẽ hiển thị:
- Header với logo và tên project
- Search box với từ khóa và tùy chọn
- Stats cards (số jobs, nguồn, công ty)
- Job cards với đầy đủ thông tin
- Pagination để chuyển trang

## 🐛 Troubleshooting

- **CORS Error**: Thêm CORS middleware vào FastAPI nếu cần
- **API không kết nối**: Kiểm tra API đang chạy tại đúng port
- **Không có dữ liệu**: Chạy spider để crawl data trước
