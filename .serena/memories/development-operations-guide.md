**COMMON COMMANDS (UPDATED)**
- Install deps: `pip install -r requirements.txt`
- Raw gate (manual): `soda scan -d postgres_db -c soda/configuration.yml soda/checks/raw_jobs.yml`
- dbt tests (post-transform): `dbt test`

**AIRFLOW DAG ORDER (EXAMPLE)**
- `soda_scan_raw` (BashOperator) → `dbt_run` (BashOperator) → `dbt_test` (BashOperator)

**TROUBLESHOOTING (NEW)**
- Soda scan fails: check schema/missing/invalid/freshness thresholds in `soda/checks/*.yml` and data in Postgres.
- Ensure `.env` matches Soda data source vars: `POSTGRES_HOST/PORT/DB/USER/PASSWORD`. 