-- Analysis: So sánh và kiểm tra chất lượng dữ liệu giữa các source

-- 1. Số lượng jobs theo từng source
select 
  source_name,
  source_site,
  count(*) as total_jobs,
  count(distinct company_name) as unique_companies,
  count(case when salary is not null then 1 end) as jobs_with_salary,
  count(case when job_deadline is not null then 1 end) as jobs_with_deadline,
  min(scraped_at) as first_scraped,
  max(scraped_at) as last_scraped
from {{ ref('stg_jobs_unified') }}
group by 1, 2
order by total_jobs desc;

-- 2. Phân bố salary types theo source
select 
  source_name,
  salary,
  count(*) as job_count
from {{ ref('stg_jobs_unified') }}
where salary in ('Negotiable', 'Competitive', 'Attractive')
group by 1, 2
order by 1, 3 desc;

-- 3. Experience levels distribution
select 
  source_name,
  experience_level,
  count(*) as job_count,
  round(count(*) * 100.0 / sum(count(*)) over (partition by source_name), 2) as percentage
from {{ ref('stg_jobs_unified') }}
where experience_level is not null
group by 1, 2
order by 1, 3 desc;

-- 4. Data completeness check
select 
  source_name,
  count(*) as total_jobs,
  
  -- Required fields
  round(count(case when job_title is not null then 1 end) * 100.0 / count(*), 2) as pct_has_title,
  round(count(case when company_name is not null then 1 end) * 100.0 / count(*), 2) as pct_has_company,
  round(count(case when job_url is not null then 1 end) * 100.0 / count(*), 2) as pct_has_url,
  
  -- Optional but important fields  
  round(count(case when salary is not null then 1 end) * 100.0 / count(*), 2) as pct_has_salary,
  round(count(case when location is not null then 1 end) * 100.0 / count(*), 2) as pct_has_location,
  round(count(case when job_description is not null then 1 end) * 100.0 / count(*), 2) as pct_has_description,
  round(count(case when requirements is not null then 1 end) * 100.0 / count(*), 2) as pct_has_requirements,
  round(count(case when benefits is not null then 1 end) * 100.0 / count(*), 2) as pct_has_benefits
  
from {{ ref('stg_jobs_unified') }}
group by 1
order by 1;

-- 5. Kiểm tra duplicates
select 
  job_url,
  count(*) as duplicate_count,
  array_agg(distinct source_name) as sources,
  min(scraped_at) as first_seen,
  max(scraped_at) as last_seen
from {{ ref('stg_jobs_unified') }}
group by 1
having count(*) > 1
order by duplicate_count desc
limit 100;

-- 6. Top companies by source
select 
  source_name,
  company_name,
  count(*) as job_count
from {{ ref('stg_jobs_unified') }}
group by 1, 2
qualify row_number() over (partition by source_name order by count(*) desc) <= 10
order by 1, 3 desc;

-- 7. Recent scraping activity
select 
  source_name,
  date(scraped_at) as scrape_date,
  count(*) as jobs_scraped,
  count(distinct company_name) as companies
from {{ ref('stg_jobs_unified') }}
where scraped_at >= current_date - interval '7 days'
group by 1, 2
order by 2 desc, 3 desc;

-- 8. Quality issues detection
select 
  source_name,
  
  -- Potential data quality issues
  count(case when length(job_title) < 5 then 1 end) as short_titles,
  count(case when length(company_name) < 3 then 1 end) as short_company_names,
  count(case when job_description is null or length(job_description) < 50 then 1 end) as missing_or_short_description,
  count(case when salary = job_type then 1 end) as salary_type_mismatch,
  count(case when job_deadline < scraped_at then 1 end) as deadline_before_scrape
  
from {{ ref('stg_jobs_unified') }}
group by 1
order by 1;
