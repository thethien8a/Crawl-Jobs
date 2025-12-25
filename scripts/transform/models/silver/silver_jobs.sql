{{ config(
    materialized='incremental',
    schema='app_layer',
    unique_key='job_id',
    on_schema_change='sync_all_columns'
) }}

WITH staged_data AS (
    SELECT * FROM {{ ref('stg_jobs') }}
    {% if is_incremental() %}
    WHERE scraped_at > (SELECT MAX(scraped_at) FROM {{ this }})
    {% endif %}
),

deduplicated AS (
    SELECT 
        *,
        -- Tạo một bản ghi duy nhất dựa trên bộ ba định danh
        ROW_NUMBER() OVER (
            PARTITION BY 
                job_title, 
                company_name, 
                source_site 
            ORDER BY scraped_at DESC
        ) as row_num
    FROM staged_data
)
SELECT
    -- Tạo một ID duy nhất cho job (Surrogate Key) để tiện quản lý sau này
    {{ dbt_utils.generate_surrogate_key([
        'job_title', 
        'company_name', 
        'source_site'
    ]) }} as job_id,   
    {{ clean_job_title('job_title') }},
    {{ clean_company('company_name') }},
    {{ clean_location('location') }},
    {{ clean_salary('salary') }},
    {{ clean_job_type('job_type') }},
    {{ clean_job_industry('job_industry') }},
    {{ clean_experience_level('experience_level') }},
    {{ clean_edu_level('education_level') }},
    {{ clean_job_position('job_position') }},
    {{ clean_des_bene_req('job_description', 'benefits', 'requirements') }},
    {{ clean_job_deadline('job_deadline') }},
    source_site,
    job_url,
    scraped_at
    
FROM deduplicated
WHERE row_num = 1