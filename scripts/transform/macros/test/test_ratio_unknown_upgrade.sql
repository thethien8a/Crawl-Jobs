{% test ratio_unknown_upgrade(model, column_name, threshold=0.1, unknown_value='Không xác định', except_source_site=none) %}

with filtered_data as (
    select *
    from {{ model }}
    {% if except_source_site %}
    where source_site not in (
        {% for site in except_source_site %}
            '{{ site }}' {%- if not loop.last %}, {% endif %}
        {% endfor %}
    )
    {% endif %}
),

metrics as (
    SELECT
        COUNT(*) FILTER (WHERE {{ column_name }} = '{{ unknown_value }}') * 1.0
        / NULLIF(COUNT(*), 0) AS ratio_unknown
    FROM filtered_data
)

select
    *
from metrics
where ratio_unknown > {{ threshold }}

{% endtest %}

