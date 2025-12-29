{% macro clean_job_title(column_name) %}
    {% set clean_col %}
        TRIM(
            REGEXP_REPLACE(
                REGEXP_REPLACE({{ column_name }}, '[-_]', ' ', 'g'                                      
                ),
                '\s+', ' ', 'g'                                          
            )
        )
    {% endset %}
    {{ clean_col }} as job_title,

    CASE 
        WHEN {{ clean_col }} ~ '(data|du lieu|dữ liệu)' THEN TRUE
        ELSE FALSE
    END as is_data_related,

    CASE
        WHEN {{ clean_col }} ~ '(engineer|kỹ sư)' THEN TRUE
        ELSE FALSE
    END as is_engineer_related,

    CASE
        WHEN {{ clean_col }} ~ '(analyst|analytics|analysis|phân tích)' THEN TRUE
        ELSE FALSE
    END as is_analyst_related,

    CASE
        WHEN {{ clean_col }} ~ '(science|scientist)' THEN TRUE
        ELSE FALSE
    END as is_scientist_related
    
{% endmacro %}
