{% macro clean_job_type(column_name) %}
    {% set clean_col = remove_accents(column_name) %}
    CASE
        WHEN {{ clean_col }} ~ '(part|thoi vu|ban thoi gian)' THEN 'Bán thời gian'
        WHEN {{ clean_col }} ~ '(intern|thuc tap|online)' THEN 'Không xác định'
        ELSE 'Toàn thời gian'
    END as job_type
{% endmacro %}