{{ config(
    materialized='table',
    schema='gold',
    post_hook=[
        "DO $$ 
         BEGIN 
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'dim_industry_pk') THEN 
                ALTER TABLE {{ this }} ADD CONSTRAINT dim_industry_pk PRIMARY KEY (industry_key); 
            END IF; 
         END $$;"
    ]
) }}

with silver_jobs as (
    select * from {{ ref('silver_jobs') }}
),

distinct_industry as (
    select distinct
        job_industry
    from silver_jobs
)

select
    {{ dbt_utils.generate_surrogate_key(['job_industry']) }} as industry_key,
    job_industry as industry_name
from distinct_industry

