{{
  config(
    materialized='incremental',
    schema='silver',
    unique_key='job_url',
    incremental_strategy='merge',
    on_schema_change='append_new_columns'
  )
}}

-- Gộp tất cả các source-specific staging models vào một bảng unified
-- Mỗi source đã được làm sạch theo logic riêng của nó

with all_sources as (
  -- JobOKO jobs
  select * from {{ ref('stg_joboko_jobs') }}
  
  union all
  
  -- TopCV jobs  
  select * from {{ ref('stg_topcv_jobs') }}
  
  union all
  
  -- VietnamWorks jobs
  select * from {{ ref('stg_vietnamworks_jobs') }}
  
  -- TODO: Thêm các source khác khi đã tạo staging models cho chúng
  -- union all
  -- select * from {{ ref('stg_itviec_jobs') }}
  -- union all
  -- select * from {{ ref('stg_linkedin_jobs') }}
  -- etc.
),

final as (
  select
    -- Primary key
    job_url,
    
    -- Job information (đã được chuẩn hóa ở layer source-specific)
    job_title,
    company_name,
    salary,
    location,
    
    -- Job details
    job_type,
    experience_level,
    education_level,
    job_industry,
    job_position,
    
    -- Content
    job_description,
    requirements,
    benefits,
    
    -- Deadline
    job_deadline,
    
    -- Metadata
    source_site,
    source_name,  -- Tên ngắn gọn của source (joboko, topcv, etc.)
    search_keyword,
    
    -- Timestamps
    scraped_at,
    scraped_date
    
  from all_sources
  {% if is_incremental() %}
    where scraped_at > (select coalesce(max(scraped_at), '1970-01-01') from {{ this }})
  {% endif %}
)

select * from final
