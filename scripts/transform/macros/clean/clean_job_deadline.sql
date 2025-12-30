{% macro clean_job_deadline(column_name) %}
    CASE
        -- 1. Format: DD/MM/YYYY hoặc D/M/YYYY (Phổ biến nhất tại Việt Nam)
        -- Chấp nhận phân cách bằng /, -, . (VD: 25/12/2025, 1-1-2025, 31.12.2025)
        WHEN {{ column_name }} ~ '\d{1,2}[/\.-]\d{1,2}[/\.-]\d{4}' THEN 
            TO_DATE(
                REPLACE(REPLACE(SUBSTRING({{ column_name }} FROM '\d{1,2}[/\.-]\d{1,2}[/\.-]\d{4}'), '.', '/'), '-', '/'), 
                'DD/MM/YYYY'
            )

        -- 2. Format: YYYY-MM-DD hoặc YYYY/MM/DD (Chuẩn ISO hoặc các site quốc tế)
        -- VD: 2025-12-25, 2025/12/25, 2025.12.25
        WHEN {{ column_name }} ~ '\d{4}[/\.-]\d{1,2}[/\.-]\d{1,2}' THEN 
            TO_DATE(
                REPLACE(REPLACE(SUBSTRING({{ column_name }} FROM '\d{4}[/\.-]\d{1,2}[/\.-]\d{1,2}'), '.', '-'), '/', '-'), 
                'YYYY-MM-DD'
            )

        -- 3. Format: DD/MM/YY (Năm có 2 chữ số)
        -- VD: 25/12/25 -> 2025-12-25
        WHEN {{ column_name }} ~ '\d{1,2}[/\.-]\d{1,2}[/\.-]\d{2}\y' 
             AND NOT {{ column_name }} ~ '\d{1,2}[/\.-]\d{1,2}[/\.-]\d{4}' THEN
            TO_DATE(
                REPLACE(REPLACE(SUBSTRING({{ column_name }} FROM '\d{1,2}[/\.-]\d{1,2}[/\.-]\d{2}\y'), '.', '/'), '-', '/'), 
                'DD/MM/YY'
            )

        -- 4. Format: Tháng/Năm (Nếu chỉ có thông tin tháng)
        -- VD: 12/2025 -> 2025-12-01
        WHEN {{ column_name }} ~ '^\d{1,2}/\d{4}$' THEN
            TO_DATE({{ column_name }}, 'MM/YYYY')
            
        ELSE NULL
    END as job_deadline
{% endmacro %}
