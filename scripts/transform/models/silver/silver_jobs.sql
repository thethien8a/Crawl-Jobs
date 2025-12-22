{{ config(
    materialized='table',
    schema='app_layer'
) }}

WITH staged_data AS (
    SELECT * FROM {{ ref('stg_jobs') }}
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
    
    job_title,
    {{ clean_company('company_name') }} as company_name
    -- location
    -- salary,
    -- job_type,
    -- experience_level,
    
    -- CASE 
    --     WHEN location LIKE '%Hà Nội%' THEN 'Hà Nội'
    --     WHEN location LIKE '%Hồ Chí Minh%' OR location LIKE '%TP.HCM%' THEN 'TP. HCM'
    --     WHEN location LIKE '%Đà Nẵng%' THEN 'Đà Nẵng'
    --     ELSE 'Tỉnh thành khác'
    -- END as city,

    -- source_site,
    -- job_url,
    -- scraped_at
    
FROM deduplicated
WHERE row_num = 1