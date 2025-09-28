{{ config(
  materialized='table',
  schema='gold'
) }}

select
  j.job_url,
  c.company_id,
  j.job_title,
  j.salary,
  j.location,
  j.job_type,
  j.experience_level,
  j.source_site,
  j.scraped_at,
  j.scraped_date
from {{ ref('stg_jobs') }} j
left join {{ ref('dim_company') }} c
  on lower(trim(regexp_replace(j.company_name, '\s+', ' ', 'g'))) = c.company_name_clean
