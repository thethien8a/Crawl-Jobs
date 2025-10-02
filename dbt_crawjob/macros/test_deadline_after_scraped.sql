{% test deadline_after_scraped(model, deadline_column, scraped_column) %}

-- Test FAILS if job deadline is before the scraped date (illogical)
SELECT *
FROM {{ model }}
WHERE {{ deadline_column }} IS NOT NULL
  AND {{ scraped_column }} IS NOT NULL
  AND {{ deadline_column }} < {{ scraped_column }}

{% endtest %}
