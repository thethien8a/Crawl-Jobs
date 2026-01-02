{{ config(
    materialized='table',
    schema='gold',
    post_hook=[
        "DO $$ 
         BEGIN 
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'dim_locations_pk') THEN 
                ALTER TABLE {{ this }} ADD CONSTRAINT dim_locations_pk PRIMARY KEY (location_key); 
            END IF; 
         END $$;"
    ]
) }}

with silver_jobs as (
    select * from {{ ref('silver_jobs') }}
),

distinct_locations as (
    select distinct
        location
    from silver_jobs
)

select
    {{ dbt_utils.generate_surrogate_key(['location']) }} as location_key,
    location as location_name
from distinct_locations

