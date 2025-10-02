{% test unique_combination(model, combination_of_columns) %}

-- Test FAILS if combination of columns has duplicates
SELECT
  {{ combination_of_columns | join(', ') }},
  COUNT(*) AS occurrences
FROM {{ model }}
GROUP BY {{ combination_of_columns | join(', ') }}
HAVING COUNT(*) > 1

{% endtest %}
