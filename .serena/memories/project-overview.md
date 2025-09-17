# Project: CrawlJob - Comprehensive Overview (Updated 2025-09-15)

## Project Identity
- **Purpose**: A professional web scraping system to collect job data, validate its quality, transform it using modern data engineering practices, store it, expose it via API, and visualize it.
- **Maturity**: Evolving from a production-ready scraping system to a Professional Data Engineering Project.

## Current Status (as of 2025-09-15)
- **Last Session Summary**: The focus was on integrating Great Expectations (GE). We have successfully established a sophisticated, code-centric approach for managing data quality.
- **Key Decisions Made**:
    - A custom object-oriented framework (`validation/GX_CLASS/gx_class.py`) will be used to programmatically control GE, instead of relying solely on the CLI.
    - The workflow is split into a definition/setup script (`checkpoints_definition.py`) and an execution script (`run_checkpoint.py`), which is ideal for automation via Airflow.
    - Project documentation (`README.md`) and memories have been updated to reflect this new, detailed structure.
- **Next Immediate Steps**: The next development session should focus on implementing the logic within the `validation/` scripts to make them fully functional. This includes:
    1.  Finalizing the `checkpoints_definition.py` script to correctly define the datasource, expectation suite, and checkpoint using `GXClass`.
    2.  Implementing the `run_checkpoint.py` script to execute a named checkpoint and return a clear pass/fail status.

## Architecture Overview
- **Data Flow** (Updated to highlight the new step):
    1.  **Orchestration**: Apache Airflow schedules the pipeline.
    2.  **Extraction**: Spiders extract raw data.
    3.  **Ingestion**: Raw data is inserted into PostgreSQL.
    4.  **(KEY) Data Quality Gate**: **Great Expectations** runs a checkpoint (triggered by `run_checkpoint.py`) to validate the raw data in PostgreSQL. The pipeline only proceeds if these checks pass.
    5.  **Transformation**: dbt transforms the validated raw data into analytics models.
    6.  **... (Storage, API, Visualization remain the same)**
