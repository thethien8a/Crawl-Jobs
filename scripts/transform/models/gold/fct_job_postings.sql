{{ config(
    materialized='incremental',
    schema='gold',
    unique_key='job_key',
    post_hook=[
        "DO $$ 
         BEGIN 
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fct_job_postings_pk') THEN 
                ALTER TABLE {{ this }} ADD CONSTRAINT fct_job_postings_pk PRIMARY KEY (job_key); 
            END IF; 
         END $$;"
    ]
) }}

with silver_jobs as (
    select * from {{ ref('silver_jobs') }}
    {% if is_incremental() %}
    where scraped_at > (select max(posted_at) from {{ this }})
    {% endif %}
),

final as (
    select
        job_id as job_key,
        stg_id,
        {{ dbt_utils.generate_surrogate_key(['company_name']) }} as company_key,
        {{ dbt_utils.generate_surrogate_key(['source_site']) }} as site_key,
        {{ dbt_utils.generate_surrogate_key(['location']) }} as location_key,
        {{ dbt_utils.generate_surrogate_key([
            'job_position',
            'job_type', 
            'estimated_seniority', 
            'education_level',
            'work_arrangement', 
            'contract_type'
        ]) }} as attribute_key,
        cast(scraped_at as date) as date_key,
        cast(job_deadline as date) as deadline_date_key,
        {{ dbt_utils.generate_surrogate_key(['job_industry']) }} as industry_key,
        -- Basic Info
        job_title,
        job_url,
        
        -- Metrics
        min_monthly_salary,
        max_monthly_salary,
        min_exp_level,
        max_exp_level,
        
        -- Category Flags
        is_data_related,
        is_engineer_related,
        is_analyst_related,
        is_scientist_related,
        has_other_industry,
        requires_english,
        
        -- Skills Flags (Boolean)
        has_sql_skills,
        has_python_skills,
        has_other_programming_skills,
        has_cloud_modern_stack_skills,
        has_big_data_streaming_skills,
        has_bi_viz_skills,
        has_ml_ai_skills,
        has_devops_skills,
        has_excel_skills,
        
        -- Benefits Flags (Boolean)
        has_financial_benefits,
        has_health_wellness_benefits,
        has_training_growth_benefits,
        has_lifestyle_culture_benefits,
        
        source_site
    from silver_jobs
)

select * from final

