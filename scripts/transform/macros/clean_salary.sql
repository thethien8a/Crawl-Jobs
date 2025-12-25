{% macro clean_salary(salary_column) %}
    -- 1. Chuẩn hóa chuỗi để trích xuất số
    {% set normalized_salary %}
        (CASE 
            WHEN {{ salary_column }} ~ '(usd|\$)' THEN REPLACE({{ salary_column }}, ',', '')
            WHEN {{ salary_column }} ~ '(tr|triệu|tỷ)' THEN REPLACE({{ salary_column }}, ',', '.') 
            ELSE REPLACE(REPLACE({{ salary_column }}, ',', ''), '.', '')
        END)
    {% endset %}

    -- 2. Hệ số thời gian (Quy đổi về tháng)
    {% set time_mult %}
        (CASE 
            WHEN {{ salary_column }} ~ 'ngày' THEN 30
            WHEN {{ salary_column }} ~ 'tuần' THEN 4
            WHEN {{ salary_column }} ~ 'năm|year' THEN 0.083
            ELSE 1
        END)
    {% endset %}

    -- 3. Hệ số đơn vị tiền tệ/độ lớn
    {% set unit_mult %}
        (CASE
            WHEN {{ salary_column }} ~ '(usd|\$)' THEN 
                CASE WHEN {{ salary_column }} ~ '(\d+k)' THEN 
                    1000 * 26000
                ELSE
                    26000
                END
            WHEN {{ salary_column }} ~ '(nghìn|k)' THEN 1000
            WHEN {{ salary_column }} ~ '(tr|triệu)' THEN 1000000
            WHEN {{ salary_column }} ~ 'tỷ' THEN 1000000000
            ELSE 1
        END)
    {% endset %}

    -- MIN SALARY
    CASE
        WHEN {{ salary_column }} IS NULL OR NOT ({{ salary_column }} ~ '\d') THEN NULL
        ELSE
            (CASE
                -- Case "đến 20": min không xác định
                WHEN {{ salary_column }} ~ '(tới|đến|upto)' AND NOT ({{ salary_column }} ~ '(từ|trên)') THEN NULL
                ELSE CAST(SUBSTRING({{ normalized_salary }} FROM '(\d+\.?\d*)') AS FLOAT)
            END) 
            * {{ time_mult }} 
            * (CASE 
                -- "Triệu ngầm": Nếu không có đơn vị text mà số nhỏ < 1000 (VD: "15" -> 15 triệu)
                WHEN NOT ({{ salary_column }} ~ '(usd|\$|nghìn|k|tr|triệu|tỷ)') 
                     AND CAST(SUBSTRING({{ normalized_salary }} FROM '(\d+\.?\d*)') AS FLOAT) < 1000 
                THEN 1000000
                ELSE {{ unit_mult }}
            END)
    END AS min_monthly_salary,

    -- MAX SALARY
    CASE
        WHEN {{ salary_column }} IS NULL OR NOT ({{ salary_column }} ~ '\d') THEN NULL
        ELSE
            (CASE
                -- Case "từ 10": max không xác định
                WHEN {{ salary_column }} ~ '(từ|trên)' AND NOT ({{ salary_column }} ~ '-') THEN NULL
                -- Khoảng "10 - 20": lấy số thứ 2
                WHEN {{ salary_column }} LIKE '%-%' THEN 
                    CAST(SUBSTRING({{ normalized_salary }} FROM '\d+\.?\d*.*?(\d+\.?\d*)') AS FLOAT)
                -- TRƯỜNG HỢP CÒN LẠI (Số đơn "10" HOẶC "đến 20"): lấy số đầu tiên làm Max
                ELSE
                    CAST(SUBSTRING({{ normalized_salary }} FROM '(\d+\.?\d*)') AS FLOAT)
            END)
            * {{ time_mult }}
            * (CASE 
                -- Kiểm tra triệu ngầm cho Max
                WHEN NOT ({{ salary_column }} ~ '(usd|\$|nghìn|k|tr|triệu|tỷ)') 
                     AND (CASE 
                            WHEN {{ salary_column }} LIKE '%-%' THEN CAST(SUBSTRING({{ normalized_salary }} FROM '\d+\.?\d*.*?(\d+\.?\d*)') AS FLOAT)
                            ELSE CAST(SUBSTRING({{ normalized_salary }} FROM '(\d+\.?\d*)') AS FLOAT)
                          END) < 1000 
                THEN 1000000
                ELSE {{ unit_mult }}
            END)
    END AS max_monthly_salary
{% endmacro %}
