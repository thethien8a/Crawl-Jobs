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
        WHEN {{ remove_accents(clean_col) }} ~ '(data|du lieu)' THEN TRUE
        ELSE FALSE
    END as is_data_related,

    CASE
        WHEN {{ remove_accents(clean_col) }} ~ '(engineer|ky su)' THEN TRUE
        ELSE FALSE
    END as is_engineer_related,

    CASE
        WHEN {{ remove_accents(clean_col) }} ~ '(analyst|analytics|analysis|ptich|phan tich)' THEN TRUE
        ELSE FALSE
    END as is_analyst_related,

    CASE
        WHEN {{ remove_accents(clean_col) }} ~ '(science|scientist)' THEN TRUE
        ELSE FALSE
    END as is_scientist_related
    
{% endmacro %}
