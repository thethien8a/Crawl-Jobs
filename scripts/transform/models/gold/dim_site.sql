{{ config(
    materialized='table',
    schema='gold',
    post_hook=[
        "DO $$ 
         BEGIN 
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'dim_site_pk') THEN 
                ALTER TABLE {{ this }} ADD CONSTRAINT dim_site_pk PRIMARY KEY (site_key); 
            END IF; 
         END $$;"
    ]
) }}

with silver_jobs as (
    select * from {{ ref('silver_jobs') }}
),

distinct_site as (
    select distinct
        source_site
    from silver_jobs
)

select
    {{ dbt_utils.generate_surrogate_key(['source_site']) }} as site_key,
    source_site
from distinct_site

