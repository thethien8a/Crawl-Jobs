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
  where source_site = 'vietnamworks.com'
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
    
    -- VietnamWorks specific: Salary handling
    -- VietnamWorks thường hiện: "You'll love it", "Up to $2000", "15-20 triệu VND"
    case 
      when salary is null or trim(salary) = '' then null
      when lower(salary) like '%you%ll love it%' then 'Attractive'
      when lower(salary) like '%thỏa thuận%' or lower(salary) like '%negotiable%' then 'Negotiable'
      when lower(salary) like '%cạnh tranh%' or lower(salary) like '%competitive%' then 'Competitive'
      -- Giữ nguyên format USD
      when salary like '%USD%' or salary like '%$%' then trim(salary)
      else trim(salary)
    end as salary,
    
    -- VietnamWorks specific: Location cleaning
    trim(
      regexp_replace(location, '\s+', ' ', 'g')
    ) as location,
    
    -- Job details
    job_type,
    
    -- VietnamWorks specific: Experience level
    case 
      when experience_level is null then null
      when lower(experience_level) like '%no experience%' or lower(experience_level) like '%entry level%' then 'Entry Level'
      when lower(experience_level) like '%experienced%' or lower(experience_level) like '%professional%' then 'Experienced'
      when lower(experience_level) like '%manager%' then 'Manager'
      when lower(experience_level) like '%senior%' then 'Senior'
      when lower(experience_level) like '%junior%' then 'Junior'
      else trim(experience_level)
    end as experience_level,
    
    -- VietnamWorks specific: Education level
    case 
      when education_level is null then null
      when lower(education_level) like '%bachelor%' or lower(education_level) like '%university%' then 'Bachelor'
      when lower(education_level) like '%college%' then 'Associate'
      when lower(education_level) like '%master%' then 'Master'
      when lower(education_level) like '%phd%' or lower(education_level) like '%doctorate%' then 'PhD'
      when lower(education_level) like '%high school%' then 'High School'
      else trim(education_level)
    end as education_level,
    
    job_industry,
    job_position,
    
    -- Content fields
    job_description,
    requirements,
    benefits,
    
    -- VietnamWorks specific: Deadline handling
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
    'vietnamworks' as source_name
    
  from source
)

select * from cleaned
