{{ config(
    materialized='table',
    schema='gold',
    post_hook=[
        "DO $$ 
         BEGIN 
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'dim_job_attributes_pk') THEN 
                ALTER TABLE {{ this }} ADD CONSTRAINT dim_job_attributes_pk PRIMARY KEY (attribute_key); 
            END IF; 
         END $$;"
    ]
) }}

with silver_jobs as (
    select * from {{ ref('silver_jobs') }}
),

distinct_attributes as (
    select distinct
        job_position,
        job_type,
        estimated_seniority,
        education_level,
        work_arrangement,
        contract_type
    from silver_jobs
)

select
    {{ dbt_utils.generate_surrogate_key([
        'job_position',
        'job_type', 
        'estimated_seniority', 
        'education_level',
        'work_arrangement', 
        'contract_type'
    ]) }} as attribute_key,
    job_position,
    job_type,
    estimated_seniority,
    education_level,
    work_arrangement,
    contract_type
from distinct_attributes

