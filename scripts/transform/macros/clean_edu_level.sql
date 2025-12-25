{% macro clean_edu_level(column_name) %}
    {% set cleaned_col = remove_accents(column_name) %}
    
    CASE
        WHEN {{ cleaned_col }} ~ 'thac si|master|tien si|doctor|prof' THEN 'Cao học'
        WHEN {{ cleaned_col }} ~ 'dai hoc|bachelor|cu nhan' THEN 'Đại học'
        WHEN {{ cleaned_col }} ~ 'cao dang|associate' THEN 'Cao đẳng'
        WHEN {{ cleaned_col }} ~ 'trung cap|nghe|vocational' THEN 'Trung cấp / Nghề'
        WHEN {{ cleaned_col }} ~ 'thpt|pho thong|cap 3|high school' THEN 'Trung học phổ thông'
        WHEN {{ cleaned_col }} ~ 'co so|cap 2' THEN 'Trung học cơ sở'
        ELSE 'Không đề cập'
    END AS education_level
{% endmacro %}

