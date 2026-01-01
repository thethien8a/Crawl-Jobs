{% test check_source_site_has_today_data(model, column_name, date_column='scraped_at') %}

with today_data as (
    select distinct {{ column_name }}
    from {{ model }}
    where {{ date_column }}::date = current_date
),

all_sources as (
    select distinct {{ column_name }}
    from {{ model }}
),

missing_sources as (
    select a.{{ column_name }}
    from all_sources a
    left join today_data t on a.{{ column_name }} = t.{{ column_name }}
    where t.{{ column_name }} is null
)

select *
from missing_sources

{% endtest %}
