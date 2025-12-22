{% macro clean_company(column_name) %}
    UPPER(
        TRIM(
            REGEXP_REPLACE(
                REGEXP_REPLACE(
                    REGEXP_REPLACE(
                        {{ column_name }},
                        -- 1. Xóa tiền tố doanh nghiệp VN (Dùng \y cho word boundary trong Postgres hỗ trợ Unicode tốt hơn)
                        '\y(cty tnhh|cty cp|cttnhh|ctcp|công ty cổ phần|công ty cp|công ty tnhh mtv|công ty tnhh|công ty mtv|tập đoàn|văn phòng đại diện|chi nhánh|ngân hàng tmcp|ngân hàng thương mại cổ phần|ngân hàng|văn phòng|công ty)\y', 
                        '', 'g'
                    ),
                    -- 2. Xóa hậu tố doanh nghiệp & địa lý
                    '\y(co\., ltd|ltd|jsc|jsc\.,|corp|corporation|inc|limited|group|vietnam|việt nam|co\.,? ltd|ltd\.?|member of viettel group)\y', 
                    '', 'g'
                ),
                -- 3. Xóa các ký tự đặc biệt thừa và dọn dẹp khoảng trắng
                '[\(\)\[\]\-\,]', ' ', 'g'
            )
        )
    )
{% endmacro %}

