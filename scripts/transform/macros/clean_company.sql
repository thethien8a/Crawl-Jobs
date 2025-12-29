{% macro clean_company(column_name) %}
    UPPER(
        TRIM(
            REGEXP_REPLACE(
                REGEXP_REPLACE(
                    REGEXP_REPLACE(
                        REGEXP_REPLACE(
                            TRIM(REGEXP_REPLACE({{ column_name }}, '\s+', ' ', 'g')), 
                            -- 1. Xóa tiền tố doanh nghiệp VN (Dùng \y cho word boundary trong Postgres hỗ trợ Unicode tốt hơn)
                            '\y( và |kỹ thuật|bưu chính| & |tổng công ty|tổng cty|cty tnhh|tư vấm|trách nhiệm hữu hạn|cty cp|cttnhh|ctcp|công ty cổ phần|công ty cp|công ty tnhh mtv|công ty tnhh|công ty mtv|tập đoàn|văn phòng đại diện|chi nhánh|ngân hàng tmcp|ngân hàng thương mại cổ phần|ngân hàng|văn phòng|công ty thương mại|và|du lịch|phát triển|giải pháp|phân tích dữ liệu|truyền hình|bất động sản|tnhh|tập đoàn|tổng bưu chính|quân đội|truyền thông|một thành viên|tài chính|tm & dv|địa ốc|chuyển phát nhanh|vàng bạc đá quý|dịch vụ|tư vấn|đầu tư|kinh doanh|công nghệ|tm dv|chuỗi nhà hàng)\y', 
                            '', 'g'
                        ),
                        -- 2. Xóa hậu tố doanh nghiệp & địa lý
                        '\y(co\., ltd|ltd|jsc|jsc\.,|corp|corporation|inc|limited|group|vietnam|việt nam|co\.,? ltd|ltd\.?|member of viettel group)\y', 
                        '', 'g'
                    ),
                    -- 3. Xóa các ký tự đặc biệt thừa
                    '[\.\(\)\[\]\-\,]', ' ', 'g'
                ),
                -- 4. Dọn dẹp khoảng trắng thừa lần cuối
                '\s+', ' ', 'g'
            )
        )
    ) AS company_name
{% endmacro %}

