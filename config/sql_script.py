
CREATE_VIEW_QUALITY_CHECK_STAGING_ZONE = """
CREATE VIEW quality_check_staging_zone AS 
WITH CTE_ERROR AS (
    SELECT
        source_site,
        created_at::date AS ngay_cao,
        COUNT(*) AS quarantine_records
    FROM quarantine_jobs
    GROUP BY source_site, ngay_cao
), CTE_STAGING AS (
    SELECT
        source_site,
        created_at::date AS ngay_cao,
        COUNT(*) AS total_pass_first_quality,
        COUNT(*) FILTER (WHERE salary IS NULL)            AS null_salary,
        COUNT(*) FILTER (WHERE requirements IS NULL)      AS null_requirements,
        COUNT(*) FILTER (WHERE benefits IS NULL)          AS null_benefits,
        COUNT(*) FILTER (WHERE job_deadline IS NULL)      AS null_job_deadline,
        COUNT(*) FILTER (WHERE search_keyword IS NULL)    AS null_search_keyword,
        COUNT(*) FILTER (WHERE job_type IS NULL)          AS null_job_type,
        COUNT(*) FILTER (WHERE job_industry IS NULL)      AS null_job_industry,
        COUNT(*) FILTER (WHERE experience_level IS NULL)  AS null_experience_level,
        COUNT(*) FILTER (WHERE education_level IS NULL)   AS null_education_level,
        COUNT(*) FILTER (WHERE job_position IS NULL)      AS null_job_position,
    FROM staging_jobs
    GROUP BY source_site, ngay_cao
)
SELECT 
    COALESCE(s.source_site, e.source_site) as source_site,
    COALESCE(s.ngay_cao, e.ngay_cao) as ngay_cao,
    COALESCE(s.total_pass_first_quality, 0) + COALESCE(e.quarantine_records, 0) as total_data,
    ROUND((COALESCE(s.total_pass_first_quality, 0)::float / NULLIF((COALESCE(s.total_pass_first_quality, 0) + COALESCE(e.quarantine_records, 0)), 0) * 100)::numeric, 2) AS pass_rate,
    ROUND((COALESCE(e.quarantine_records, 0)::float / NULLIF((COALESCE(s.total_pass_first_quality, 0) + COALESCE(e.quarantine_records, 0)), 0) * 100)::numeric, 2) AS quarantine_rate,
    COALESCE(s.null_salary, 0) as null_salary,
    COALESCE(s.null_requirements, 0) as null_requirements,
    COALESCE(s.null_benefits, 0) as null_benefits,
    COALESCE(s.null_job_deadline, 0) as null_job_deadline,
    COALESCE(s.null_search_keyword, 0) as null_search_keyword,
    COALESCE(s.null_job_type, 0) as null_job_type,
    COALESCE(s.null_job_industry, 0) as null_job_industry,
    COALESCE(s.null_experience_level, 0) as null_experience_level,
    COALESCE(s.null_education_level, 0) as null_education_level,
    COALESCE(s.null_job_position, 0) as null_job_position,
FROM 
    CTE_STAGING s
    FULL OUTER JOIN CTE_ERROR e
    ON s.source_site = e.source_site AND s.ngay_cao = e.ngay_cao
"""

SELECT_QUALITY_CHECK_STAGING_ZONE = "SELECT * FROM quality_check_staging_zone"
