{% macro clean_experience_level(column_name) %}
    {% set clean_col = remove_accents(column_name) %}
    
    {% set clean_col_final = "REGEXP_REPLACE(" ~ clean_col ~ ", '(\\,)', '.', 'g')" %}

    CASE
        WHEN {{ clean_col }} IS NULL OR NOT ({{ clean_col }} ~ '\d') THEN 0
        ELSE
            (CASE
                WHEN {{ clean_col }} ~ '(less|duoi)' THEN 0
                WHEN {{ clean_col }} ~ '(occupational)' THEN
                    CAST(SUBSTRING({{clean_col_final}} FROM '(\d+\.?\d*)') AS FLOAT) /12
                ELSE
                    CAST(SUBSTRING({{clean_col_final}} FROM '(\d+\.?\d*)') AS FLOAT)
            END)
    END as min_exp_level,
    
    CASE
        WHEN {{ clean_col }} IS NULL THEN NULL
        WHEN {{ clean_col }} ~ '(khong yeu cau kn| khong ycau| khong yc| ko ycau)' THEN 0
        ELSE
            (CASE
                WHEN {{ clean_col }} LIKE '%-%' THEN
                    CAST(SUBSTRING({{clean_col_final}} FROM '\d+\.?\d*.*?(\d+\.?\d*)') AS FLOAT)
                WHEN {{ clean_col }} ~ '(less|duoi)' THEN 
                    CAST(SUBSTRING({{clean_col_final}} FROM '(\d+\.?\d*)') AS FLOAT)
                ELSE
                    NULL
            END)
    END as max_exp_level
{% endmacro %}
