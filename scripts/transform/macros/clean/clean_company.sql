{% macro clean_company(column_name) %}
    UPPER(
        TRIM(
            REGEXP_REPLACE(
                REGEXP_REPLACE(
                    REGEXP_REPLACE(
                        REGEXP_REPLACE(
                            TRIM(REGEXP_REPLACE({{ column_name }}, '\s+', ' ', 'g')), 
                            -- 1. Xóa tiền tố doanh nghiệp VN (Dùng \y cho word boundary trong Postgres hỗ trợ Unicode tốt hơn)
                            '\y(hệ thống|giáo dục|đào tạo|kỹ thuật|bưu chính|sản xuất|thương mại|bảo hiểm|nhân thọ|tổng công ty|tổng cty|cty tnhh|tư vấn|xây dựng|trách nhiệm hữu hạn|cty cp|cttnhh|ctcp|công ty cổ phần|công ty cp|công ty tnhh mtv|công ty tnhh|công ty mtv|tập đoàn|văn phòng đại diện|chi nhánh|ngân hàng tmcp|ngân hàng thương mại cổ phần|ngân hàng|văn phòng|công ty thương mại|và|du lịch|công ty|phát triển|giải pháp|phân tích dữ liệu|truyền hình|bất động sản|tnhh|tập đoàn|tổng bưu chính|quân đội|viễn thông|truyền thông|một thành viên|tài chính|tm & dv|tmdv|địa ốc|chuyển phát nhanh|vàng bạc đá quý|dịch vụ|tư vấn|đầu tư|dược phẩm|kinh doanh|công nghiệp|vận tải|công nghệ|tm dv|chứng khoán|1 thành viên|chuỗi nhà hàng|cổ phần)\y', 
                            '', 'g'
                        ),
                        -- 2. Xóa hậu tố doanh nghiệp & địa lý
                        '\y(https?://[^\s]+|co\., ltd| và |\||ltd|jsc| & |số |jsc\.,|corp|corporation|inc|limited|group|vietnam|việt nam|co\.,? ltd|ltd\.?|member of viettel group)\y', 
                        ' ', 'g'
                    ),
                    -- 3. Xóa các ký tự đặc biệt thừa
                    '[\.\(\)\[\]\-\,\/]', ' ', 'g'
                ),
                -- 4. Dọn dẹp khoảng trắng thừa lần cuối
                '\s+', ' ', 'g'
            )
        )
    ) AS company_name
{% endmacro %}

