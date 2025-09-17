**KEY FILES (UPDATED)**
- Soda configs: `soda/configuration.yml`, `soda/checks/raw_jobs.yml`

**KEY COMMANDS (UPDATED)**
- Raw gating (Soda): `soda scan -d postgres_db -c soda/configuration.yml soda/checks/raw_jobs.yml`
- dbt tests: `dbt test`

**ENV VARS**
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` used by Soda data source.

**PIPELINE ORDER**
- Soda gate → dbt run → dbt test → publish DuckDB → Superset refresh.