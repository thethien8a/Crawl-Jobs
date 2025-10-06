-- ==========================================
-- DATA QUALITY CHECKS: Hybrid Staging Model
-- ==========================================
-- Quality checks for the hybrid staging model (stg_jobs)

-- ========================================
-- 1. Overall Statistics
-- ========================================
select
  count(*) as total_rows,
  count(distinct source_name) as unique_sources,
  count(distinct company_name) as unique_companies,
  min(scraped_at) as earliest_data,
  max(scraped_at) as latest_data,
  max(scraped_date) as latest_scrape_date
from {{ ref('stg_jobs') }};

-- ========================================
-- 2. Per-Source Statistics
-- ========================================
select
  source_name,
  source_site,
  count(*) as total_jobs,
  count(distinct company_name) as unique_companies,
  count(case when salary is not null then 1 end) as jobs_with_salary,
  count(case when job_deadline is not null then 1 end) as jobs_with_deadline,
  min(scraped_at) as first_scraped,
  max(scraped_at) as last_scraped
from {{ ref('stg_jobs') }}
group by 1, 2
order by total_jobs desc;
-- ========================================
-- 3. Field Completeness by Source
-- ========================================
select 
  source_name,
  count(*) as total,
  round(count(salary) * 100.0 / count(*), 2) as pct_has_salary,
  round(count(experience_level) * 100.0 / count(*), 2) as pct_has_experience,
  round(count(education_level) * 100.0 / count(*), 2) as pct_has_education,
  round(count(job_deadline) * 100.0 / count(*), 2) as pct_has_deadline,
  round(count(job_description) * 100.0 / count(*), 2) as pct_has_description
from {{ ref('stg_jobs') }}
group by source_name
order by source_name;

-- ========================================
-- 4. Salary Normalization Check
-- ========================================
select 
  source_name,
  salary,
  count(*) as count
from {{ ref('stg_jobs') }}
where salary in ('Negotiable', 'Competitive', 'Attractive')
group by source_name, salary
order by source_name, salary;-- ========================================
-- 5. Experience Level Distribution
-- ========================================
select 
  source_name,
  experience_level,
  count(*) as count,
  round(count(*) * 100.0 / sum(count(*)) over (partition by source_name), 2) as percentage
from {{ ref('stg_jobs') }}
where experience_level is not null
group by source_name, experience_level
order by source_name, count desc;

-- ========================================
-- 6. Recent Data Check (Last 7 Days)
-- ========================================
select
  source_name,
  date(scraped_at) as scrape_date,
  count(*) as jobs_scraped,
  count(distinct company_name) as companies
from {{ ref('stg_jobs') }}
where scraped_at >= current_date - interval '7 days'
group by source_name, scrape_date
order by scrape_date desc, jobs_scraped desc;

-- ========================================
-- 7. Data Quality Issues Detection
-- ========================================
select 
  source_name,
  count(case when length(job_title) < 5 then 1 end) as short_titles,
  count(case when length(company_name) < 3 then 1 end) as short_company_names,
  count(case when job_description is null or length(job_description) < 50 then 1 end) as missing_or_short_description,
  count(case when job_deadline < scraped_at then 1 end) as deadline_before_scrape
from {{ ref('stg_jobs') }}
group by source_name
order by source_name;

-- ========================================
-- 8. Top Companies by Source
-- ========================================
select 
  source_name,
  company_name,
  count(*) as job_count
from {{ ref('stg_jobs') }}
group by source_name, company_name
qualify row_number() over (partition by source_name order by count(*) desc) <= 10
order by source_name, job_count desc;
