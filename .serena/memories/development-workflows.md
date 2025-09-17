# Development Workflows - CrawlJob Project (Updated 2025-09-15)

## 🔄 **PRODUCTION DEVELOPMENT WORKFLOWS**

### **(NEW) Programmatic Data Quality Workflow (User-Defined)**

This project uses a custom, code-based workflow to manage Great Expectations, centered around the `GXClass` wrapper.

#### **Phase 1: Setup & Definition (Developer Task)**
1.  **Develop `GXClass`**: The core `validation/GX_CLASS/gx_class.py` is the central library. Developers can extend this class with new methods to interact with the Great Expectations API.
2.  **Define Components**: The developer runs the `validation/checkpoints_definition.py` script. This script utilizes `GXClass` to programmatically:
    - Connect to the PostgreSQL datasource.
    - Define data assets (e.g., the `jobs` table).
    - Create Expectation Suites and add specific expectations.
    - Build and save Checkpoint configurations.
    This step is analogous to using the GE CLI but is fully managed in code, allowing for version control of the entire setup process.

#### **Phase 2: Execution (Automated & Manual)**
1.  **Manual Execution for Testing**: A developer can test a data quality check by running the execution script directly from the terminal.
    ```bash
    # Example command to be run from the project root
    python -m validation.run_checkpoint <your_checkpoint_name>
    ```
    *(Note: Using `-m` flag is recommended to ensure Python's path resolution works correctly from the project root.)*

2.  **Automated Execution (via Airflow)**: In production, the Airflow DAG will trigger the same execution script.
    ```bash
    # Command within an Airflow BashOperator
    python /path/to/project/validation/run_checkpoint.py <your_checkpoint_name>
    ```
    The script is responsible for returning an appropriate exit code (`0` for success, `1` for failure) to signal the outcome to Airflow, thus acting as a Data Quality Gate in the pipeline.

### **Updated End-to-End Data Pipeline Workflow**
1.  **Airflow**: Triggers the pipeline.
2.  **Task 1 (Scrapy)**: Collects data into PostgreSQL.
3.  **Task 2 (Great Expectations)**: Airflow calls `python validation/run_checkpoint.py raw_jobs_checkpoint`.
    - **On PASS**: The pipeline proceeds.
    - **On FAIL**: The pipeline stops, and an alert is sent.
4.  **Task 3 (dbt)**: Transforms the validated data.
5.  ... (rest of the pipeline).
