{% test salary_has_currency(model, column_name) %}

-- Test FAILS if salary doesn't contain currency or is in unexpected format
SELECT *
FROM {{ model }}
WHERE {{ column_name }} IS NOT NULL
  AND {{ column_name }} != 'Negotiate'
  AND {{ column_name }} != 'Negotiable'
  AND NOT (
    {{ column_name }} LIKE '%VND%'
    OR {{ column_name }} LIKE '%USD%'
    OR {{ column_name }} LIKE '%$%'
    OR {{ column_name }} LIKE '%VNĐ%'
  )

{% endtest %}
