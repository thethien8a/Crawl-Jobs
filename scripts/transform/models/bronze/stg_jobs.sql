WITH raw_data AS (
    SELECT * FROM {{ source('scrapy_raw', 'staging_jobs') }}
)

SELECT
    TRIM(LOWER(job_title)) AS job_title,
    TRIM(LOWER(company_name)) AS company_name,
    COALESCE(LOWER(salary), 'Thỏa thuận') AS salary,
    TRIM(LOWER(location)) AS location,
    COALESCE(LOWER(job_type), 'Không đề cập') AS job_type,
    COALESCE(NULLIF(TRIM(LOWER(job_industry)), ''), 'Không đề cập') AS job_industry,
    COALESCE(LOWER(experience_level), 'Không đề cập') AS experience_level,
    COALESCE(LOWER(education_level), 'Không đề cập') AS education_level,
    COALESCE(LOWER(job_position), 'Không đề cập') AS job_position,
    COALESCE(LOWER(job_description), 'Không đề cập') AS job_description,
    COALESCE(LOWER(requirements), 'Không đề cập') AS requirements,
    COALESCE(job_deadline, '2099-12-31') AS job_deadline, -- Mặc định là ngày rất xa nếu không có deadline
    source_site,
    job_url,
    CAST(scraped_at AS DATE) AS scraped_at -- Thêm cái này chủ yếu cho an toàn
FROM
    raw_data
