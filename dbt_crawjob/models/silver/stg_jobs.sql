{{ config(
  materialized='incremental',
  schema='silver',
  unique_key=['job_url','scraped_date'],
  incremental_strategy='merge'
) }}

with src as (
  select
    job_url,
    -- Normalize job_title: trim, remove extra spaces, handle null
    trim(regexp_replace(job_title, '\s+', ' ', 'g')) as job_title,

    -- Normalize company_name: trim, lowercase, remove extra spaces
    lower(trim(regexp_replace(company_name, '\s+', ' ', 'g'))) as company_name,

    -- Handle salary: keep as is or standardize format if needed
    salary,

    -- Normalize location: trim, handle common variations
    trim(regexp_replace(location, '\s+', ' ', 'g')) as location,

    -- Keep other fields as is but ensure consistency
    job_type,
    experience_level,
    education_level,
    job_industry,
    job_position,
    job_description,
    requirements,
    benefits,
    job_deadline,
    source_site,
    search_keyword,
    scraped_at,
    date(scraped_at) as scraped_date

  from {{ source('bronze','jobs') }}
  {% if is_incremental() %}
  where scraped_at > (select coalesce(max(scraped_at),'1970-01-01') from {{ this }})
  {% endif %}
)
select * from src
