import os
from datetime import datetime, timedelta

from airflow.operators.bash import BashOperator

from airflow import DAG

default_args = {
    "owner": "data-eng",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="crawljob_pipeline",
    default_args=default_args,
    description="Crawl → Raw Gate (Soda) → Sync (DuckDB) → Transform (dbt) → Test (dbt) → Publish",
    schedule_interval="0 2 * * *",
    start_date=datetime(2025, 1, 1),
    catchup=False,
) as dag:

    # 1) Run spiders (assumes venv activated in Airflow worker env)
    run_spiders = BashOperator(
        task_id="run_spiders",
        bash_command="python /opt/airflow/dags/run_spider.py --spider all --keyword 'IT'",
        env={
            **os.environ,
        },
    )

    # 2) Raw data gating with Soda Core (Sequential checks)
    soda_scan_check1 = BashOperator(
        task_id="soda_scan_check1",
        bash_command=(
            "soda scan -d postgres_db -c /opt/airflow/dags/soda/configuration.yml "
            "/opt/airflow/dags/soda/checks/raw_jobs_check1.yml"
        ),
        env={
            **os.environ,
        },
    )

    soda_scan_check2 = BashOperator(
        task_id="soda_scan_check2",
        bash_command=(
            "soda scan -d postgres_db -c /opt/airflow/dags/soda/configuration.yml "
            "/opt/airflow/dags/soda/checks/raw_jobs_check2.yml"
        ),
        env={
            **os.environ,
        },
    )

    soda_scan_check3 = BashOperator(
        task_id="soda_scan_check3",
        bash_command=(
            "soda scan -d postgres_db -c /opt/airflow/dags/soda/configuration.yml "
            "/opt/airflow/dags/soda/checks/raw_jobs_check3.yml"
        ),
        env={
            **os.environ,
        },
    )

    # 3) Sync Postgres → DuckDB using postgres_scanner
    duckdb_sync = BashOperator(
        task_id="duckdb_sync",
        bash_command=(
            "python /opt/airflow/dags/scripts/sync_pg_to_duckdb.py"
        ),
        env={
            **os.environ,
            # Optional: override defaults via env, e.g. SYNC_MODE=full
            # "SYNC_MODE": "incremental",
            # "PG_TABLE": "jobs",
            # "PG_CURSOR_COLUMN": "scraped_at",
            # "DUCKDB_SCHEMA": "raw",
        },
    )

    # 4) Transform with dbt
    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dags/dbt && dbt run",
        env={
            **os.environ,
        },
    )

    # 5) Tests with dbt
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/dags/dbt && dbt test",
        env={
            **os.environ,
        },
    )

    (
        run_spiders
        >> soda_scan_check1
        >> soda_scan_check2
        >> soda_scan_check3
        >> duckdb_sync
        >> dbt_run
        >> dbt_test
    )
