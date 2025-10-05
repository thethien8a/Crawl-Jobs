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
  where source_site = 'vn.joboko.com'
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
    
    -- JobOKO specific: Salary handling
    -- JobOKO thường có format: "Thỏa thuận" hoặc "10 - 15 triệu"
    case 
      when salary is null or trim(salary) = '' then null
      when lower(salary) like '%thỏa thuận%' or lower(salary) like '%negotiable%' then 'Negotiable'
      when lower(salary) like '%cạnh tranh%' or lower(salary) like '%competitive%' then 'Competitive'
      else trim(salary)
    end as salary,
    
    -- JobOKO specific: Location cleaning
    -- Loại bỏ prefix "Khu vực:" hoặc "Địa điểm:" nếu có
    trim(
      regexp_replace(
        regexp_replace(location, '(Khu vực|Địa điểm):\s*', '', 'gi'),
        '\s+', ' ', 'g'
      )
    ) as location,
    
    -- Job details
    job_type,
    
    -- JobOKO specific: Experience level normalization
    case 
      when experience_level is null then null
      when lower(experience_level) like '%không yêu cầu%' or lower(experience_level) like '%no experience%' then 'Entry Level'
      when lower(experience_level) like '%dưới 1 năm%' then '< 1 year'
      when lower(experience_level) like '%1-2 năm%' or lower(experience_level) like '%1 - 2%' then '1-2 years'
      when lower(experience_level) like '%2-5 năm%' or lower(experience_level) like '%2 - 5%' then '2-5 years'
      when lower(experience_level) like '%trên 5 năm%' or lower(experience_level) like '%> 5%' then '5+ years'
      else trim(experience_level)
    end as experience_level,
    
    education_level,
    job_industry,
    job_position,
    
    -- Content fields
    job_description,
    requirements,
    benefits,
    
    -- JobOKO specific: Deadline handling
    -- Chuẩn hóa format ngày tháng
    case 
      when job_deadline is null or trim(job_deadline) = '' then null
      when job_deadline ~ '^\d{1,2}/\d{1,2}/\d{4}$' then job_deadline
      else null
    end as job_deadline,
    
    -- Metadata
    source_site,
    search_keyword,
    
    -- Timestamps
    scraped_at,
    date(scraped_at) as scraped_date,
    
    -- Add source identifier
    'joboko' as source_name
    
  from source
)

select * from cleaned
