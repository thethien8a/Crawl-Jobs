# 🔧 macros/ - SQL Functions tùy chỉnh

## Tác dụng
Chứa các macro (function) SQL có thể tái sử dụng.

## Chức năng
- Tạo các function SQL tùy chỉnh như `cent_to_dollars`, `clean_string`, etc.
- Giúp tránh duplicate code
- Có thể sử dụng lại across multiple models

## Cách sử dụng
Gọi trong models bằng `{{ my_macro('parameter') }}`