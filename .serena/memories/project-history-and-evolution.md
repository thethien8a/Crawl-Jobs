**DECISION LOG (NEW)**
- [2025-09-16] Replaced Great Expectations with hybrid validation:
  - Soda Core for raw data gating (Postgres),
  - dbt tests for business validation after transforms.
  - Reasons: simpler stack with dbt, clear separation of concerns, fail-fast on raw, easier Airflow integration.

**EVOLUTION**
- Added `/soda/` configs; updated dependencies and README to document 2-layer validation.