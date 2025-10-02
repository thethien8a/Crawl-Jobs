{% test row_count_in_range(model, min_rows=1, max_rows=1000000) %}

-- Test FAILS if table row count is outside expected range
WITH row_count AS (
  SELECT COUNT(*) AS total
  FROM {{ model }}
)
SELECT *
FROM row_count
WHERE total < {{ min_rows }}
   OR total > {{ max_rows }}

{% endtest %}
