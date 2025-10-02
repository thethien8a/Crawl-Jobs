{% test is_recent(model, column_name, days_ago=7) %}

-- Test FAILS if timestamp is older than X days or NULL
SELECT *
FROM {{ model }}
WHERE {{ column_name }} < CURRENT_DATE - INTERVAL '{{ days_ago }}' DAYS
   OR {{ column_name }} IS NULL

{% endtest %}
