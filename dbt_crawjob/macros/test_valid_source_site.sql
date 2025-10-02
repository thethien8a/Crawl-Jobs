{% test valid_source_site(model, column_name) %}

-- Test FAILS if source_site is not in the valid list
WITH valid_sites AS (
  SELECT unnest([
    'topcv', 'itviec', 'careerlink', 'careerviet',
    'job123', 'joboko', 'jobsgo', 'jobstreet',
    'linkedin', 'vietnamworks'
  ]) AS site
)
SELECT *
FROM {{ model }}
WHERE {{ column_name }} NOT IN (SELECT site FROM valid_sites)
   OR {{ column_name }} IS NULL

{% endtest %}
