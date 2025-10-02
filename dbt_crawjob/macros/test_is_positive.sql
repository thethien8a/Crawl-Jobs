{% test is_positive(model, column_name) %}

-- Test FAILS if value is <= 0 or NULL
SELECT *
FROM {{ model }}
WHERE {{ column_name }} <= 0
   OR {{ column_name }} IS NULL

{% endtest %}
