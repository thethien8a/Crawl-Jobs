{{ config(
    materialized='table',
    schema='gold',
    post_hook=[
        "DO $$ 
         BEGIN 
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'dim_companies_pk') THEN 
                ALTER TABLE {{ this }} ADD CONSTRAINT dim_companies_pk PRIMARY KEY (company_key); 
            END IF; 
         END $$;"
    ]
) }}

with silver_jobs as (
    select * from {{ ref('silver_jobs') }}
),

distinct_companies as (
    select distinct
        company_name
    from silver_jobs
)

select
    {{ dbt_utils.generate_surrogate_key(['company_name']) }} as company_key,
    company_name
from distinct_companies

