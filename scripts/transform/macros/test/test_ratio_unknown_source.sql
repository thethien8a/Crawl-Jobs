{% test ratio_unknown_source(model, column_name, unknown_value='Không xác định', threshold=0.01, source_site=none)%}

with filtered_data as (
    select *
    from {{ model }}
    where scraped_at::date = current_date
    {% if source_site %}
    AND source_site = '{{ source_site }}'
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

