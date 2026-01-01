{% test ratio_empty_multi(model, column_name, site_thresholds) %}

with base as (
    select 
        source_site,
        {{ column_name }}
    from {{ model }}
    where scraped_at::date = current_date
),

site_stats as (
    select
        source_site,
        COUNT(*) FILTER (WHERE {{ column_name }} = '' OR {{ column_name }} is null) * 1.0 
        / NULLIF(COUNT(*), 0) AS actual_ratio
    from base
    group by 1
),

thresholds as (
    {% for site, threshold in site_thresholds.items() %}
    select 
        '{{ site }}' as source_site, 
        {{ threshold }} as threshold
    {% if not loop.last %} union all {% endif %}
    {% endfor %}
)

select 
    s.source_site,
    s.actual_ratio,
    t.threshold
from site_stats s
join thresholds t on s.source_site = t.source_site
where s.actual_ratio > t.threshold

{% endtest %}

