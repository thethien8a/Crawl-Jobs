from datetime import timedelta
import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator

DBT_PROJECT_DIR = "scripts/transform"

# Cấu hình mặc định cho DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Khởi tạo DAG
with DAG(
    'crawl_and_transform_pipeline',
    default_args=default_args,
    description='Pipeline: Scrapy Crawl -> DBT Test Source -> DBT Run Int -> DBT Test Int -> DBT Run Silver',
    schedule_interval='0 15 * * *',
    start_date=pendulum.datetime(2026, 1, 1, tz='Asia/Ho_Chi_Minh'),
    catchup=False,
    tags=['scrapy', 'dbt', 'etl'],
) as dag:

    extract_and_load = BashOperator(
        task_id='extract_and_load_data',
        # Có thể chạy tất cả spider bằng cách thêm --spider all ví dụ: python -m scripts.extract_and_load.run_spider --spider all
        bash_command='python -m scripts.extract_and_load.run_spider --spider linkedin', 
        cwd='/opt/airflow',
        env={'PYTHONPATH': '/opt/airflow'}
    )


    test_source_staging = BashOperator(
        task_id='dbt_test_source_staging',
        bash_command='dbt test --select source:scrapy_raw.staging_jobs --profiles-dir profiles',
        cwd=DBT_PROJECT_DIR,
        retries=0, # Task fail cái thì thôi luôn
    )

    run_int_jobs_cleaned = BashOperator(
        task_id='dbt_run_int_jobs_cleaned',
        bash_command='dbt run --select int_jobs_cleaned --profiles-dir profiles',
        cwd=DBT_PROJECT_DIR
    )

    test_int_jobs_cleaned = BashOperator(
        task_id='dbt_test_int_jobs_cleaned',
        bash_command='dbt test --select int_jobs_cleaned --profiles-dir profiles',
        cwd=DBT_PROJECT_DIR,
        retries=0, # Task fail cái thì thôi luôn
    )

    run_quality_check = BashOperator(
        task_id='run_quality_check',
        bash_command='python -m scripts.quality_check.staging_check',
        cwd='/opt/airflow',
        env={'PYTHONPATH': '/opt/airflow'}
    )

    generate_quality_check_gate = BashOperator(
        task_id='generate_quality_check_gate',
        bash_command='python -m scripts.quality_check.gate_check',
        cwd='/opt/airflow',
        env={'PYTHONPATH': '/opt/airflow'}
    )
    
    generate_elementary_report = BashOperator(
        task_id='generate_elementary_report',
        bash_command=(
            '/opt/dbt_venv/bin/edr report '
            '--profiles-dir profiles '
            '--open-browser false '  
            '--file-path /opt/airflow/scripts/transform/edr_target/elementary_report.html'
        ),
        cwd=DBT_PROJECT_DIR,
        retries=0,  # Không retry nếu fail
        trigger_rule='all_done'
    )

    run_silver_jobs = BashOperator(
        task_id='dbt_run_silver_jobs',
        bash_command='dbt run --select silver_jobs+ --profiles-dir profiles',
        cwd=DBT_PROJECT_DIR,
    )
    
    extract_and_load >> [test_source_staging, run_quality_check]
    [test_source_staging, run_quality_check] >> run_int_jobs_cleaned
    run_int_jobs_cleaned >> [test_int_jobs_cleaned, generate_quality_check_gate]
    test_int_jobs_cleaned >> [generate_elementary_report, run_silver_jobs]
