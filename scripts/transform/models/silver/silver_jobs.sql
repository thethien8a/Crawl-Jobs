{{ config(
    materialized='incremental',
    schema='app_layer',
    unique_key='job_id',
    on_schema_change='sync_all_columns',
    post_hook=[
        "DO $$ 
         BEGIN 
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'silver_jobs_pk') THEN 
                ALTER TABLE {{ this }} ADD CONSTRAINT silver_jobs_pk PRIMARY KEY (job_id); 
            END IF; 
         END $$;",
        "CREATE EXTENSION IF NOT EXISTS pg_trgm;",
        "CREATE INDEX IF NOT EXISTS idx_silver_jobs_scraped_at ON {{ this }} (scraped_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_silver_jobs_location ON {{ this }} (location);",
        "CREATE INDEX IF NOT EXISTS idx_silver_jobs_job_type ON {{ this }} (job_type);",
        "CREATE INDEX IF NOT EXISTS idx_silver_jobs_work_arrangement ON {{ this }} (work_arrangement);",
        "CREATE INDEX IF NOT EXISTS idx_silver_jobs_trgm_title ON {{ this }} USING GIN (job_title gin_trgm_ops);",
        "CREATE INDEX IF NOT EXISTS idx_silver_jobs_trgm_position ON {{ this }} USING GIN (job_position gin_trgm_ops);",
        "CREATE INDEX IF NOT EXISTS idx_silver_jobs_fts_title ON {{ this }} USING GIN (to_tsvector('english', COALESCE(job_title, '')));",
        "CREATE INDEX IF NOT EXISTS idx_silver_jobs_fts_position ON {{ this }} USING GIN (to_tsvector('english', COALESCE(job_position, '')));"
    ]
) }}

WITH cleaned_data AS (
    SELECT * FROM {{ ref('int_jobs_cleaned') }}
    {% if is_incremental() %}
    WHERE scraped_at > (SELECT MAX(scraped_at) FROM {{ this }})
    {% endif %}
),

deduplicated AS (
    SELECT 
        *,
        -- Tạo một bản ghi duy nhất dựa trên bộ ba định danh
        ROW_NUMBER() OVER (
            PARTITION BY 
                job_title, 
                company_name, 
                source_site 
            ORDER BY scraped_at DESC
        ) as row_num
    FROM cleaned_data
)
SELECT
    *
FROM deduplicated
WHERE row_num = 1