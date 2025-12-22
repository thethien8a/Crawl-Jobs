# 📊 models/ - Trái tim của dbt

## Tác dụng
Chứa các file SQL định nghĩa transformations (biến đổi dữ liệu).

## Chức năng
- Chứa logic chính để transform dữ liệu từ raw data thành business-ready data
- Khi chạy `dbt run`, các model này sẽ được compile và execute
- Thường được tổ chức theo các layer: `staging` → `intermediate` → `marts`

## Trong dự án này
Có thư mục `example/` với các model mẫu để tham khảo.