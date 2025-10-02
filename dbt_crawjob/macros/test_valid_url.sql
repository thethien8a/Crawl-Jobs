{% test valid_url(model, column_name) %}

-- Test FAILS if URL doesn't start with http:// or https://
SELECT *
FROM {{ model }}
WHERE {{ column_name }} IS NOT NULL
  AND NOT (
    {{ column_name }} LIKE 'http://%'
    OR {{ column_name }} LIKE 'https://%'
  )

{% endtest %}
