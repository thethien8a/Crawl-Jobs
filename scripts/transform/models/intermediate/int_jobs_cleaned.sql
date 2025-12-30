{{ config(
    materialized='incremental',
    schema='intermediate_bronze_silver',
    unique_key='job_url',
    on_schema_change='sync_all_columns',
    indexes=[
      {'columns': ['job_title', 'company_name', 'source_site', 'scraped_at']},
      {'columns': ['scraped_at']},
      {'columns': ['company_name']}
    ]
) }}

WITH raw_data AS (
    SELECT * FROM {{ source('scrapy_raw', 'staging_jobs') }}
    {% if is_incremental() %}
    WHERE scraped_at > (SELECT MAX(scraped_at) FROM {{ this }})
    {% endif %}
),
deduplicated AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY job_url
            ORDER BY scraped_at DESC
        ) as business_key_rank
    FROM raw_data
),

cleaned_fields AS (
    SELECT
        id AS stg_id,
        {{ clean_job_title("TRIM(LOWER(job_title))") }},
        {{ clean_company("TRIM(LOWER(company_name))") }},
        {{ clean_location("TRIM(LOWER(location))") }},
        {{ clean_salary("LOWER(salary)") }},
        {{ clean_job_type("COALESCE(LOWER(job_type), 'không đề cập')") }},
        {{ clean_job_industry("COALESCE(NULLIF(TRIM(LOWER(job_industry)), ''), 'không đề cập')") }},
        {{ clean_experience_level("LOWER(experience_level)") }},
        {{ clean_edu_level("LOWER(education_level)") }},
        {{ clean_job_position("LOWER(job_position)") }},
        {{ clean_des_bene_req(
            "COALESCE(LOWER(job_description), 'không đề cập')", 
            "COALESCE(LOWER(benefits), 'không đề cập')", 
            "COALESCE(LOWER(requirements), 'không đề cập')"
        ) }},
        {{ clean_job_deadline('job_deadline') }},
        source_site,
        job_url,
        CAST(scraped_at AS timestamp) AS scraped_at
    FROM deduplicated 
    WHERE business_key_rank = 1
)

SELECT
    {{ dbt_utils.generate_surrogate_key([
        'job_title', 
        'company_name', 
        'source_site'
    ]) }} AS job_id,
    *
FROM cleaned_fields
WHERE company_name <> ''

