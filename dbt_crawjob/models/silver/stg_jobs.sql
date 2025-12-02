{{
  config(
    materialized='incremental',
    schema='silver',
    unique_key= ['job_title', 'company_name', 'location', 'source_site'],
    incremental_strategy='merge',
    on_schema_change='append_new_columns',
    tags=['staging', 'hybrid']
  )
}}

with source as (
  select *
  from {{ source('bronze', 'jobs') }}
  {% if is_incremental() %}
    where scraped_at > (select coalesce(max(scraped_at), '1970-01-01') from {{ this }})
  {% endif %}
),

base_cleaning as (
  select
    job_url,
    
    -- Common text normalization
    {{ normalize_job_title('job_title') }} as job_title,
    lower({{ clean_whitespace('company_name') }}) as company_name,
    {{ clean_whitespace('location') }} as location_raw,
    
    -- Keep raw values for source-specific processing
    salary as salary_raw,
    experience_level as experience_raw,
    education_level as education_raw,
    job_deadline as deadline_raw,
    
    -- Simple fields (no source-specific logic needed)
    job_type,
    job_industry,
    job_position,
    job_description,
    requirements,
    benefits,
    search_keyword,
    
    -- Metadata & timestamps
    source_site,
    scraped_at,
    date(scraped_at) as scraped_date
    
  from source
),

-- ========================================
-- STEP 2: Source-specific normalization
-- ========================================
source_specific as (
  select
    job_url,
    job_title,
    company_name,
    
    -- ========== LOCATION CLEANING ==========
    case 
      -- JobOKO: Remove "Khu vực:" or "Địa điểm:" prefix
      when source_site = 'vn.joboko.com' then
        trim(regexp_replace(
          regexp_replace(location_raw, '(Khu vực|Địa điểm):\s*', '', 'gi'),
          '\s+', ' ', 'g'
        ))
      
      -- Other sources: Just trim
      else trim(location_raw)
    end as location,
    
    -- ========== SALARY NORMALIZATION ==========
    case 
      -- JobOKO specific patterns
      when source_site = 'vn.joboko.com' then
        case
          when salary_raw is null or trim(salary_raw) = '' then null
          when lower(salary_raw) like '%thỏa thuận%' or lower(salary_raw) like '%negotiable%' then 'Negotiable'
          when lower(salary_raw) like '%cạnh tranh%' or lower(salary_raw) like '%competitive%' then 'Competitive'
          else trim(salary_raw)
        end
      
      -- TopCV specific patterns
      when source_site = 'topcv.vn' then
        case
          when salary_raw is null or trim(salary_raw) = '' then null
          when lower(salary_raw) like '%thỏa thuận%' or lower(salary_raw) like '%thoa thuan%' then 'Negotiable'
          when lower(salary_raw) like '%cạnh tranh%' then 'Competitive'
          when lower(salary_raw) like '%up to%' then trim(salary_raw)
          when salary_raw ~ '\d+\s*-\s*\d+\s*triệu' then regexp_replace(salary_raw, '\s+', ' ', 'g')
          else trim(salary_raw)
        end
      
      -- VietnamWorks specific patterns
      when source_site = 'vietnamworks.com' then
        case
          when salary_raw is null or trim(salary_raw) = '' then null
          when lower(salary_raw) like '%you%ll love it%' then 'Attractive'
          when lower(salary_raw) like '%thỏa thuận%' or lower(salary_raw) like '%negotiable%' then 'Negotiable'
          when lower(salary_raw) like '%cạnh tranh%' or lower(salary_raw) like '%competitive%' then 'Competitive'
          when salary_raw like '%USD%' or salary_raw like '%$%' then trim(salary_raw)
          else trim(salary_raw)
        end
      
      -- Default for other sources (ITviec, LinkedIn, etc.)
      else
        case
          when salary_raw is null or trim(salary_raw) = '' then null
          when lower(salary_raw) like '%thỏa thuận%' or lower(salary_raw) like '%negotiable%' then 'Negotiable'
          when lower(salary_raw) like '%cạnh tranh%' or lower(salary_raw) like '%competitive%' then 'Competitive'
          else trim(salary_raw)
        end
    end as salary,
    
    -- ========== EXPERIENCE LEVEL NORMALIZATION ==========
    case 
      -- JobOKO specific patterns
      when source_site = 'vn.joboko.com' then
        case
          when experience_raw is null then null
          when lower(experience_raw) like '%không yêu cầu%' or lower(experience_raw) like '%no experience%' then 'Entry Level'
          when lower(experience_raw) like '%dưới 1 năm%' then '< 1 year'
          when lower(experience_raw) like '%1-2 năm%' or lower(experience_raw) like '%1 - 2%' then '1-2 years'
          when lower(experience_raw) like '%2-5 năm%' or lower(experience_raw) like '%2 - 5%' then '2-5 years'
          when lower(experience_raw) like '%trên 5 năm%' or lower(experience_raw) like '%> 5%' then '5+ years'
          else trim(experience_raw)
        end
      
      -- TopCV specific patterns
      when source_site = 'topcv.vn' then
        case
          when experience_raw is null then null
          when lower(experience_raw) like '%chưa có kinh nghiệm%' or lower(experience_raw) like '%không yêu cầu%' then 'Entry Level'
          when lower(experience_raw) like '%dưới 1 năm%' then '< 1 year'
          when lower(experience_raw) like '%1 năm%' then '1 year'
          when lower(experience_raw) like '%2 năm%' then '2 years'
          when lower(experience_raw) like '%3 năm%' then '3 years'
          when lower(experience_raw) like '%4 năm%' then '4 years'
          when lower(experience_raw) like '%5 năm%' then '5 years'
          when lower(experience_raw) like '%trên 5 năm%' then '5+ years'
          else trim(experience_raw)
        end
      
      -- VietnamWorks specific patterns (English terms)
      when source_site = 'vietnamworks.com' then
        case
          when experience_raw is null then null
          when lower(experience_raw) like '%no experience%' or lower(experience_raw) like '%entry level%' then 'Entry Level'
          when lower(experience_raw) like '%experienced%' or lower(experience_raw) like '%professional%' then 'Experienced'
          when lower(experience_raw) like '%manager%' then 'Manager'
          when lower(experience_raw) like '%senior%' then 'Senior'
          when lower(experience_raw) like '%junior%' then 'Junior'
          else trim(experience_raw)
        end
      
      -- Default for other sources
      else
        case
          when experience_raw is null then null
          when lower(experience_raw) like '%không yêu cầu%' or lower(experience_raw) like '%no experience%' or lower(experience_raw) like '%entry level%' then 'Entry Level'
          else trim(experience_raw)
        end
    end as experience_level,
    
    -- ========== EDUCATION LEVEL NORMALIZATION ==========
    case 
      -- TopCV specific (has most detailed education mapping)
      when source_site = 'topcv.vn' then
        case
          when education_raw is null then null
          when lower(education_raw) like '%đại học%' then 'Bachelor'
          when lower(education_raw) like '%cao đẳng%' then 'Associate'
          when lower(education_raw) like '%trung cấp%' then 'Vocational'
          when lower(education_raw) like '%thạc sĩ%' or lower(education_raw) like '%master%' then 'Master'
          when lower(education_raw) like '%tiến sĩ%' or lower(education_raw) like '%phd%' then 'PhD'
          when lower(education_raw) like '%không yêu cầu%' then 'Not Required'
          else trim(education_raw)
        end
      
      -- VietnamWorks specific (English terms)
      when source_site = 'vietnamworks.com' then
        case
          when education_raw is null then null
          when lower(education_raw) like '%bachelor%' or lower(education_raw) like '%university%' then 'Bachelor'
          when lower(education_raw) like '%college%' then 'Associate'
          when lower(education_raw) like '%master%' then 'Master'
          when lower(education_raw) like '%phd%' or lower(education_raw) like '%doctorate%' then 'PhD'
          when lower(education_raw) like '%high school%' then 'High School'
          else trim(education_raw)
        end
      
      -- Default for other sources
      else trim(education_raw)
    end as education_level,
    
    -- ========== JOB DEADLINE NORMALIZATION ==========
    -- All sources use same pattern: DD/MM/YYYY
    {{ normalize_deadline('deadline_raw') }} as job_deadline,
    
    -- ========== SOURCE NAME MAPPING ==========
    case 
      when source_site = 'vn.joboko.com' then 'joboko'
      when source_site = 'topcv.vn' then 'topcv'
      when source_site = 'vietnamworks.com' then 'vietnamworks'
      when source_site = 'itviec.vn' then 'itviec'
      when source_site like '%linkedin%' then 'linkedin'
      when source_site like '%careerlink%' then 'careerlink'
      when source_site like '%careerviet%' then 'careerviet'
      when source_site like '%job123%' then 'job123'
      when source_site like '%jobsgo%' then 'jobsgo'
      when source_site like '%jobstreet%' then 'jobstreet'
      else 'unknown'
    end as source_name,
    
    -- Simple passthrough fields
    job_type,
    job_industry,
    job_position,
    job_description,
    requirements,
    benefits,
    search_keyword,
    source_site,
    scraped_at,
    scraped_date
    
  from base_cleaning
),

-- ========================================
-- STEP 3: Final selection with column ordering
-- ========================================
final as (
  select
    -- Primary key
    job_url,
    
    -- Job basic information
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
    
    -- Job content
    job_description,
    requirements,
    benefits,
    
    -- Job deadline
    job_deadline,
    
    -- Metadata
    source_site,
    source_name,
    search_keyword,
    
    -- Timestamps
    scraped_at,
    scraped_date
    
  from source_specific
)

select * from final
