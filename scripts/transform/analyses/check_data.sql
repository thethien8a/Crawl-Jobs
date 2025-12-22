with source_data as (
    select * from {{ ref('stg_jobs') }}
),
SELECT * FROM source_data