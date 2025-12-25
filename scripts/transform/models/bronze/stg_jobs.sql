WITH raw_data AS (
    SELECT * FROM {{ source('scrapy_raw', 'staging_jobs') }}
)

SELECT
    TRIM(LOWER(job_title)) AS job_title,
    TRIM(LOWER(company_name)) AS company_name,
    LOWER(salary) AS salary,
    TRIM(LOWER(location)) AS location,
    COALESCE(LOWER(job_type), 'không đề cập') AS job_type,
    COALESCE(NULLIF(TRIM(LOWER(job_industry)), ''), 'không đề cập') AS job_industry,
    LOWER(experience_level) AS experience_level,
    LOWER(education_level) AS education_level,
    LOWER(job_position) AS job_position,
    COALESCE(LOWER(job_description), 'không đề cập') AS job_description,
    COALESCE(LOWER(requirements), 'không đề cập') AS requirements,
    COALESCE(LOWER(benefits), 'không đề cập') AS benefits,
    job_deadline,
    source_site,
    job_url,
    CAST(scraped_at AS timestamp) AS scraped_at -- Thêm cái này chủ yếu cho an toàn
FROM
    raw_data
