**FILES & DIRECTORIES (UPDATED)**
- `/soda/`
  - `configuration.yml` – Soda Core data source (Postgres) via .env vars
  - `checks/raw_jobs.yml` – raw gating checks (schema, missing, invalid, row_count, freshness)
- `/CrawlJob/` – Scrapy project (spiders, pipelines, settings)
- `/api/` – FastAPI server
- `/plan/` – Stack plan
- `requirements.txt` – deps (now includes Soda Core, removed GE)

**NAV SHORTCUTS (NEW)**
- Soda configs: `soda/configuration.yml`, `soda/checks/raw_jobs.yml`
- Run raw gate: `soda scan -d postgres_db -c soda/configuration.yml soda/checks/raw_jobs.yml`