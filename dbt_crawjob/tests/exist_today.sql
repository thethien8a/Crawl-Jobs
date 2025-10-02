-- tests/exist_today.sql
-- This test should PASS if data exists for CURRENT_DATE, and FAIL if no data exists.
SELECT
    'No data scraped for today' AS error_message
FROM (
    SELECT COUNT(*) as total
    FROM {{ source('bronze', 'jobs') }}
    WHERE scraped_date = CURRENT_DATE
)
WHERE total = 0
