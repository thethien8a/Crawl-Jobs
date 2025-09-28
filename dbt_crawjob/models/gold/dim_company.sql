{{ config(
  materialized='table',
  schema='gold'
) }}

select
  row_number() over (order by company_name_clean) as company_id,
  company_name as company_name_raw,
  lower(trim(regexp_replace(company_name, '\s+', ' ', 'g'))) as company_name_clean
from (
  select distinct company_name
  from {{ ref('stg_jobs') }}
  where company_name is not null
)
