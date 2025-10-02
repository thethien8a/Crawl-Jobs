**TESTING STRATEGY AND QUALITY ASSURANCE**

**Testing Philosophy:**
- **Comprehensive Coverage**: Unit, integration, and end-to-end testing for all pipeline components
- **Data Quality First**: Validation at every layer (raw, bronze, silver, gold)
- **Automation Priority**: All tests runnable in CI/CD pipeline
- **Real-world Simulation**: Use actual spider outputs and database states

**Testing Levels:**

**1. Unit Tests (Spider Logic)**
- **Scope**: Individual spider parsing, item validation, pipeline processing
- **Tools**: pytest, scrapy.testing
- **Coverage**:
  - Spider parse methods (parse_search, parse_job)
  - Item field validation
  - Pipeline item processing
  - Middleware functionality
- **Examples**:
  ```python
  def test_topcv_parse_job(self):
      spider = TopcvSpider()
      response = self.get_response('topcv_job_page.html')
      items = list(spider.parse_job(response))
      self.assertEqual(len(items), 1)
      self.assertEqual(items[0]['job_title'], 'Expected Title')

  def test_postgresql_pipeline_process_item(self):
      pipeline = PostgreSQLPipeline()
      item = JobItem(job_title='Test Job', company_name='Test Co')
      result = pipeline.process_item(item, None)
      self.assertIsNotNone(result)
  ```

**2. Integration Tests (Pipeline Components)**
- **Scope**: End-to-end data flow from spider to database
- **Tools**: pytest, testcontainers (for PostgreSQL/DuckDB)
- **Coverage**:
  - Full spider run with mock responses
  - Database insertion and retrieval
  - Soda Core validation execution
  - dbt model execution and output verification
- **Examples**:
  ```python
  def test_full_spider_pipeline(self):
      # Mock spider run
      process = CrawlerProcess()
      process.crawl(TopcvSpider, keyword='test')
      # Verify database has expected data
      # Verify Soda checks pass
      # Verify dbt models build successfully
  ```

**3. End-to-End Tests (Full Pipeline)**
- **Scope**: Complete data pipeline execution
- **Tools**: pytest, Docker Compose (for full stack)
- **Coverage**:
  - Spider execution → PostgreSQL storage → Soda validation → DuckDB sync → dbt transformation → BI query
  - Performance benchmarks (processing time, memory usage)
  - Error handling and recovery
- **Examples**:
  ```python
  def test_daily_pipeline_e2e(self):
      # Run spiders
      # Execute Soda checks
      # Sync to DuckDB
      # Run dbt models
      # Query resulting analytics tables
      # Assert data quality metrics
  ```

**Data Quality Assurance:**

**1. Soda Core (Raw Data Validation)**
- **Sequential Checks**: raw_jobs_check1.yml → check2.yml → check3.yml
- **Coverage**:
  - Schema validation (required columns, data types)
  - Duplicate detection
  - Missing value checks
  - Source-specific field validation
  - Spider coverage (all 10 sites present)
- **Automation**: Integrated into Airflow DAG, stops pipeline on failure

**2. dbt Tests (Transformed Data Validation)**
- **Schema Tests**: not_null, unique, accepted_values
- **Referential Integrity**: Relationships between dim/fact tables
- **Business Rules**: Salary ranges, location formats, industry categories
- **Examples**:
  ```yaml
  models:
    - name: fct_jobs
      tests:
        - relationships:
            to: ref('dim_company')
            field: company_id
        - not_null:
            column_name: job_url
  ```

**Quality Gates:**

**1. Pre-Production Gates**
- All unit tests pass (pytest)
- All integration tests pass
- Code coverage > 80%
- No linting errors (black, isort)
- Data quality checks pass (Soda + dbt tests)

**2. Production Gates**
- Pipeline runs successfully in staging environment
- Performance benchmarks met (processing time < 2 hours)
- Data freshness verified (last successful run < 24 hours)
- Error rates monitored (spider failures, sync failures)

**Monitoring and Alerting:**

**1. Data Quality Monitoring**
- Daily Soda scans with alerts on failure
- dbt test failures trigger notifications
- Data freshness checks (scraped_at recency)

**2. Performance Monitoring**
- Spider execution times
- Database query performance
- Pipeline step durations
- Memory and CPU usage

**3. Error Tracking**
- Spider blocking detection (429, CAPTCHA)
- Database connection failures
- Transformation errors
- BI query failures

**Testing Environments:**

**1. Development**
- Local PostgreSQL/DuckDB
- Manual test runs
- Debug mode enabled

**2. Staging**
- Docker Compose stack
- Automated pipeline runs
- Performance testing

**3. Production**
- Full Airflow orchestration
- Monitoring and alerting
- Backup and recovery procedures

**Test Data Management:**

**1. Test Datasets**
- Sample job listings from each site
- Edge cases (missing fields, special characters)
- Performance test data (large volumes)

**2. Data Masking**
- Remove personal information from test data
- Use synthetic data for sensitive fields

**3. Data Refresh**
- Weekly refresh of test datasets
- Automated cleanup of test databases

**Quality Metrics:**

**1. Data Completeness**
- Percentage of required fields populated
- Spider coverage (all sites active)

**2. Data Accuracy**
- Field validation pass rates
- Cross-reference checks

**3. Data Timeliness**
- Average age of data
- Pipeline execution frequency

**4. System Reliability**
- Pipeline success rate
- Error recovery time
- Uptime metrics