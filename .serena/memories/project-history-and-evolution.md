**HISTORY UPDATE (September 2025 - Major Simplification)**

**Recent Changes:**
- ✅ Removed Makefile from project (simplified development workflow)
- ✅ Simplified code quality tooling to Black + isort only (removed flake8/mypy)
- ✅ Updated pyproject.toml to only configure Black and isort
- ✅ Documented manual workflow commands (without make)
- ⚠️ Identified API inconsistency: uses SQL Server while pipeline uses PostgreSQL

**Adopted Airbyte for EL:**
- Switched to Airbyte for EL from PostgreSQL (OLTP) to DuckDB (OLAP)
- Migrated transform strategy to dbt-duckdb (no cross-database dbt)
- Updated diagrams and README to reflect Airbyte → DuckDB → dbt-duckdb flow
- Retained sequential Soda Core validation pre-sync

**Current Architecture:**
Scrapy → PostgreSQL (raw) → Soda Core → Airbyte → DuckDB → dbt-duckdb → Superset
FastAPI → SQL Server (⚠️ inconsistency - should be PostgreSQL)

**Airflow Orchestration:**
- Sequential DAG: spiders → soda → airbyte → dbt → superset
- Manual commands available for local development
- Simplified tooling for faster development cycles

**Code Quality Evolution:**
- Started with: Black + isort + flake8 + mypy (comprehensive)
- Simplified to: Black + isort only (faster, less overhead)
- Focus on auto-formatting and import organization
- Removed linting/type-checking for speed

**Key Milestones:**
1. ✅ Initial project setup with 10 spiders
2. ✅ PostgreSQL integration and Soda validation
3. ✅ Airflow orchestration implementation
4. ✅ Airbyte EL pipeline setup
5. ✅ DuckDB OLAP integration
6. ✅ Simplified development tooling
7. 🔄 API migration to PostgreSQL (pending)
8. ⏳ dbt-duckdb models creation
9. ⏳ Superset dashboard integration

**Future Direction:**
- Complete API migration to PostgreSQL for consistency
- Implement dbt-duckdb transformation models
- Add Superset BI dashboards
- Consider re-adding Makefile if team grows or workflow becomes complex