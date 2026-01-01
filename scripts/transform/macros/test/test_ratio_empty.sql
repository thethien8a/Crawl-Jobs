{% test ratio_empty(model, column_name, threshold=0.01, source_site=none)%}

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
        COUNT(*) FILTER (WHERE {{ column_name }} = '' OR {{ column_name }} is null) * 1.0
        / NULLIF(COUNT(*), 0) AS ratio_empty
    FROM filtered_data
)

select
    *
from metrics
where ratio_empty > {{ threshold }}

{% endtest %}

