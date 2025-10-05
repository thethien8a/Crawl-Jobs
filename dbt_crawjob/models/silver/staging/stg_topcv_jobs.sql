{{
  config(
    materialized='incremental',
    schema='silver',
    unique_key='job_url',
    incremental_strategy='merge',
    on_schema_change='append_new_columns'
  )
}}

with source as (
  select *
  from {{ source('bronze', 'jobs') }}
  where source_site = 'topcv.vn'
  {% if is_incremental() %}
    and scraped_at > (select coalesce(max(scraped_at), '1970-01-01') from {{ this }})
  {% endif %}
),

cleaned as (
  select
    -- Primary keys
    job_url,
    
    -- Normalized job information
    trim(regexp_replace(job_title, '\s+', ' ', 'g')) as job_title,
    lower(trim(regexp_replace(company_name, '\s+', ' ', 'g'))) as company_name,
    
    -- TopCV specific: Salary handling
    -- TopCV format: "Thỏa thuận", "15 - 20 triệu", "Up to 2000 USD"
    case 
      when salary is null or trim(salary) = '' then null
      when lower(salary) like '%thỏa thuận%' or lower(salary) like '%thoa thuan%' then 'Negotiable'
      when lower(salary) like '%cạnh tranh%' then 'Competitive'
      when lower(salary) like '%up to%' then trim(salary)
      -- Chuẩn hóa format triệu VND
      when salary ~ '\d+\s*-\s*\d+\s*triệu' then regexp_replace(salary, '\s+', ' ', 'g')
      else trim(salary)
    end as salary,
    
    -- TopCV specific: Location cleaning
    -- TopCV có thể có format: "Hà Nội, Hồ Chí Minh" hoặc chi tiết địa chỉ
    trim(
      regexp_replace(location, '\s+', ' ', 'g')
    ) as location,
    
    -- Job details
    job_type,
    
    -- TopCV specific: Experience level normalization
    case 
      when experience_level is null then null
      when lower(experience_level) like '%chưa có kinh nghiệm%' or lower(experience_level) like '%không yêu cầu%' then 'Entry Level'
      when lower(experience_level) like '%dưới 1 năm%' then '< 1 year'
      when lower(experience_level) like '%1 năm%' then '1 year'
      when lower(experience_level) like '%2 năm%' then '2 years'
      when lower(experience_level) like '%3 năm%' then '3 years'
      when lower(experience_level) like '%4 năm%' then '4 years'
      when lower(experience_level) like '%5 năm%' then '5 years'
      when lower(experience_level) like '%trên 5 năm%' then '5+ years'
      else trim(experience_level)
    end as experience_level,
    
    -- TopCV specific: Education level
    case 
      when education_level is null then null
      when lower(education_level) like '%đại học%' then 'Bachelor'
      when lower(education_level) like '%cao đẳng%' then 'Associate'
      when lower(education_level) like '%trung cấp%' then 'Vocational'
      when lower(education_level) like '%thạc sĩ%' or lower(education_level) like '%master%' then 'Master'
      when lower(education_level) like '%tiến sĩ%' or lower(education_level) like '%phd%' then 'PhD'
      when lower(education_level) like '%không yêu cầu%' then 'Not Required'
      else trim(education_level)
    end as education_level,
    
    job_industry,
    job_position,
    
    -- Content fields
    job_description,
    requirements,
    benefits,
    
    -- TopCV specific: Deadline handling
    case 
      when job_deadline is null or trim(job_deadline) = '' then null
      -- TopCV format: "DD/MM/YYYY" hoặc "Còn X ngày"
      when job_deadline ~ '^\d{1,2}/\d{1,2}/\d{4}$' then job_deadline
      when lower(job_deadline) like '%còn%ngày%' then null -- Không parse được, để null
      else null
    end as job_deadline,
    
    -- Metadata
    source_site,
    search_keyword,
    
    -- Timestamps
    scraped_at,
    date(scraped_at) as scraped_date,
    
    -- Add source identifier
    'topcv' as source_name
    
  from source
)

select * from cleaned
