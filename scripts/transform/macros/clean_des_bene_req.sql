{% macro clean_des_bene_req(description_column, benefits_column, requirements_column) %}
    -- Gộp và làm sạch văn bản ban đầu
    {% set combined_text %}
        COALESCE({{ description_column }}, '') || ' ' || 
        COALESCE({{ benefits_column }}, '') || ' ' || 
        COALESCE({{ requirements_column }}, '')
    {% endset %}

    {% set cleaned_text %}
        TRIM(REGEXP_REPLACE(LOWER({{ combined_text }}), '\s+', ' ', 'g'))
    {% endset %}

    -- Văn bản đã xóa dấu để dễ dàng matching từ khóa tiếng Việt
    {% set normalized_text %}
        {{ remove_accents(cleaned_text) }}
    {% endset %}

    {{ cleaned_text }} as job_full_content,

    -- ========================================
    -- 1. KỸ NĂNG CÔNG NGHỆ (TECH STACK - GROUPED)
    -- ========================================
    
    -- SQL & Databases (Cốt lõi)
    CASE 
        WHEN {{ normalized_text }} ~ '\y(sql|plsql|tsql|postgres|mysql|oracle|mongodb|nosql|query|postgresql)\y' THEN TRUE 
        ELSE FALSE 
    END as has_sql_skills,

    -- Python (Cốt lõi)
    CASE 
        WHEN {{ normalized_text }} ~ '\y(python|py|pandas|numpy|scikit|pytorch|tensorflow|keras|scipy|polars|dask|jupyter|pyspark)\y' THEN TRUE 
        ELSE FALSE 
    END as has_python_skills,

    -- Các ngôn ngữ lập trình khác (R, Java, Scala, JS, C++, Go...)
    CASE 
        WHEN {{ normalized_text }} ~ '\y(r|rstudio|java|scala|kotlin|jvm|javascript|js|node\.js|typescript|react\.js|vue\.js|angular|golang|rust|c\+\+)\y' THEN TRUE 
        ELSE FALSE 
    END as has_other_programming_skills,

    -- Cloud & Modern Data Stack (AWS, Azure, GCP, Snowflake, Databricks, dbt, Airflow...)
    CASE 
        WHEN {{ normalized_text }} ~ '\y(aws|azure|gcp|google\s?cloud|snowflake|databricks|dbt|airflow|fivetran|stitch|matillion|synapse|redshift|bigquery|adf|adls|s3|ec2|lambda|cloud)\y' THEN TRUE 
        ELSE FALSE 
    END as has_cloud_modern_stack_skills,

    -- Big Data & Real-time (Spark, Hadoop, Kafka, Lakehouse...)
    CASE 
        WHEN {{ normalized_text }} ~ '\y(spark|hadoop|hdfs|yarn|hive|kafka|flink|beam|iceberg|hudi|delta\s?lake|lakehouse|streaming|real\s?time|event\s?streaming|kinesis)\y' THEN TRUE 
        ELSE FALSE 
    END as has_big_data_streaming_skills,

    -- BI & Visualization (Power BI, Tableau, Looker, v.v.)
    CASE 
        WHEN {{ normalized_text }} ~ '\y(power\s?bi|tableau|looker|metabase|superset|viz|dashboard|bi\s?tool|qlik|redash|finebi|chart\.js|plotly|streamlit|gradio)\y' THEN TRUE 
        ELSE FALSE 
    END as has_bi_viz_skills,

    -- AI / Machine Learning / GenAI
    CASE 
        WHEN {{ normalized_text }} ~ '\y(machine\s?learning|ml|ai|deep\s?learning|neural|nlp|computer\s?vision|llm|generative|gen\s?ai|transformer|bert|gpt|mlops|modeling)\y' THEN TRUE 
        ELSE FALSE 
    END as has_ml_ai_skills,

    -- Công nghệ phần mềm & DevOps (Git, Docker, CI/CD, API...)
    CASE 
        WHEN {{ normalized_text }} ~ '\y(git|github|gitlab|version\s?control|docker|kubernetes|k8s|ci\s?cd|jenkins|terraform|api|rest\s?api|testing|unit\s?test|qa)\y' THEN TRUE 
        ELSE FALSE 
    END as has_\_devops_skills,

    -- ========================================
    -- 2. PHÚC LỢI & MÔI TRƯỜNG (BENEFITS & PERKS - GROUPED)
    -- ========================================

    -- Tài chính & Thưởng (Bonus, 13th month, ESOP, Lì xì, Phụ cấp...)
    CASE 
        WHEN {{ normalized_text }} ~ '(thuong|bonus|thang\s?13|lixi|thuong\s?quy|thuong\s?nam|performance\s?bonus|stock|esop|equity|phu\s?cap|allowance|tro\s?cap|com\s?trua|an\s?trua|gui\s?xe)' THEN TRUE 
        ELSE FALSE 
    END as has_financial_benefits,

    -- Sức khỏe & Bảo hiểm (Healthcare, Insurance, Gym...)
    CASE 
        WHEN {{ normalized_text }} ~ '(bao\s?hiem|insurance|social\s?security|healthcare|suc\s?khoe|medical|dental|gym|the\s?thao|kham\s?suc\s?khoe)' THEN TRUE 
        ELSE FALSE 
    END as has_health_wellness_benefits,

    -- Đào tạo & Phát triển (Training, Courses, Certificates, Thăng tiến...)
    CASE 
        WHEN {{ normalized_text }} ~ '(dao\s?tao|training|learning|course|certificate|chung\s?chi|phat\s?trien|hoc\s?bong|thang\s?tien|career\s?path|mentoring)' THEN TRUE 
        ELSE FALSE 
    END as has_training_growth_benefits,

    -- Môi trường & Thiết bị (Team building, Du lịch, Macbook, Laptop, Pantry...)
    CASE 
        WHEN {{ normalized_text }} ~ '(du\s?lich|trip|team\s?building|nghi\s?mat|snack|pantry|tra\s?ca\s?phe|macbook|laptop|thiet\s?bi|van\s?phong|modern\s?office)' THEN TRUE 
        ELSE FALSE 
    END as has_lifestyle_culture_benefits,

    -- ========================================
    -- 3. VAI TRÒ & CẤP BẬC (ROLES & SENIORITY)
    -- ========================================

    CASE 
        WHEN {{ normalized_text }} ~ '(senior|truong\s?nhom|chu\s?tri|lead|principal|staff|chuyen\s?gia|bac\s?cao|architect)' THEN 'Senior/Lead'
        WHEN {{ normalized_text }} ~ '(junior|moi\s?tot\s?nghiep|fresher|intern|thuc\s?tap|entry|associate)' THEN 'Junior/Fresher'
        ELSE 'Mid/Professional'
    END as estimated_seniority,

    -- Hình thức làm việc
    CASE 
        WHEN {{ normalized_text }} ~ '(remote|lam\s?tu\s?xa|tai\s?nha|wfhoh|from\s?home)' THEN 'Remote'
        WHEN {{ normalized_text }} ~ '(hybrid|linh\s?hoat|ket\s?hop|flexible)' THEN 'Hybrid'
        ELSE 'On-site'
    END as work_arrangement,

    -- Loại hợp đồng
    CASE 
        WHEN {{ normalized_text }} ~ '(full\s?time|fulltime|fte|permanent|hop\s?dong\s?chinh\s?thuc)' THEN 'Full-time'
        WHEN {{ normalized_text }} ~ '(part\s?time|parttime|ban\s?thoi\s?gian)' THEN 'Part-time'
        WHEN {{ normalized_text }} ~ '(contract|contractor|hop\s?dong\s?thoi\s?vu|temporary)' THEN 'Contract'
        WHEN {{ normalized_text }} ~ '(freelance|freelancer|tu\s?do|independent)' THEN 'Freelance'
        ELSE 'Not Specified'
    END as contract_type,

    CASE 
        WHEN {{ normalized_text }} ~ '\y(english|tieng\s?anh|ielts|toeic|toefl|communication|fluency|proficient)\y' THEN TRUE 
        ELSE FALSE 
    END as requires_english,

    CASE 
        WHEN {{ normalized_text }} ~ '\y(excel|spreadsheet|google\s?sheet|vba|pivot|vlookup|advanced\s?excel)\y' THEN TRUE 
        ELSE FALSE 
    END as has_excel_skills

{% endmacro %}
