# LLM Understanding Guide - CrawlJob Project (Updated 2025-09-12)

## CORE WORKFLOW (with Data Quality Gate)
1.  **Input Processing**: User provides a keyword.
2.  **Spider Execution**: Spiders collect data.
3.  **Data Extraction**: Raw data is parsed from HTML/JS.
4.  **Storage**: Data is loaded into a raw `jobs` table in PostgreSQL.
5.  **(NEW) Data Quality Gate**: A **Great Expectations Checkpoint** is run against the raw data in PostgreSQL.
    - **If PASS**: The pipeline continues.
    - **If FAIL**: The pipeline stops and an alert is raised. This prevents bad data from moving downstream.
6.  **Data Transformation (dbt)**: If data quality checks pass, dbt transforms the raw data into analytics-ready models.
7.  **API Serving & Analytics**: FastAPI serves the clean, raw data, while tools like Superset analyze the transformed models.

## KEY COMPONENTS BREAKDOWN

### **(NEW) 6. Data Validation System (great_expectations/ & validation/)**
- **great_expectations/**: This is the auto-managed "Data Context" for GE. It stores all configurations for datasources, expectation suites, and checkpoints.
- **validation/run_checkpoint.py**: This is the dedicated script used by the automation layer (Airflow) to trigger a data quality check. It acts as the bridge between the orchestrator and the GE framework.

---
*(Rest of the guide remains largely the same, but the context of "Data Quality" is now a formal, automated step in the process rather than a manual best practice.)*
