# Architecture Patterns - CrawlJob System (Updated 2025-09-05, with DE Stack Integration)

## Overall Architecture Pattern
**Modular Monolith with Modern Data Stack Integration**
- Scrapy project as the core scraping engine.
- FastAPI service as the data access layer.
- Web dashboard as the presentation layer.
- **Apache Airflow** for workflow orchestration.
- **dbt** for data transformation.
- **Great Expectations** for data quality validation.
- **PostgreSQL** as the OLTP (Online Transaction Processing) database for raw data, running in Docker.
- **DuckDB** as the OLAP (Online Analytical Processing) database for analytics marts.
- **Apache Superset** for BI dashboards.

## 🆕 **Spider Architecture Evolution**

### **Multi-Strategy Pattern Implementation**
**Before**: Hybrid approaches with mixed technologies.
**After**: Pure technology stacks with clear categorization, integrated into an Airflow-orchestrated pipeline.

### **Spider Categories & Patterns**

#### **1. Simple Scrapy Spiders (6 sites)**
**Strategy**: Pure Scrapy Request/Response Pattern
- JobsGO, JobOKO, 123job, CareerViet, JobStreet, CareerLink
- **Pattern**: Standard Scrapy selectors with fallback logic
- **Technology**: Scrapy + CSS Selectors + XPath
- **Use Case**: Static HTML content with minimal JavaScript

#### **2. Enhanced Scrapy Spiders (1 site)**
**Strategy**: Scrapy + JavaScript Extraction Pattern
- TopCV: Advanced JavaScript object parsing
- **Pattern**: `window.qgTracking` JavaScript extraction + HTML fallback
- **Technology**: Scrapy + JavaScript evaluation + CSS selectors
- **Use Case**: Dynamic content with JavaScript data objects

#### **3. Pure Selenium Spiders (3 sites)**
**Strategy**: Browser Automation Pattern (Updated)\n- LinkedIn, ITviec, VietnamWorks (Pure Selenium)
- **Pattern**: Full browser control with WebDriver API, anti-detection techniques.
- **Technology**: Selenium WebDriver + ChromeDriver + Anti-detection
- **Use Case**: Complex JavaScript, authentication, dynamic content

### **New: Selenium-Only Parsing Pattern**
**Problem Solved**: Hybrid dependency complexity and performance overhead.
**Implementation**:
```python
def _extract_job_data_with_selenium(self, job_url):
    def safe_get_text(selector, by=By.CSS_SELECTOR):
        \"\"\"Universal safe text extraction with error handling\"\"\"\n        try:\n            element = self._driver.find_element(by, selector)\n            return element.text.strip()\n        except (NoSuchElementException, Exception):\n            return ''\n    \n    def get_text_by_xpath_text(label_text):
        \"\"\"Advanced text-based element location\"\"\"\n        try:\n            xpath = f\"//*[contains(text(), '{label_text}')]/following-sibling::*[1]\"\n            element = self._driver.find_element(By.XPATH, xpath)\n            return element.text.strip()\n        except (NoSuchElementException, Exception):\n            return ''\n    \n    # All parsing uses direct WebDriver calls\n    item['job_title'] = safe_get_text(\"h1[name='title']\")\n    item['company_name'] = safe_get_text(\"a[href*='nha-tuyen-dung']\")\n    item['job_type'] = get_text_by_xpath_text(\"LOẠI HÌNH LÀM VIỆC\")\n```
**Benefits**:\n- ✅ **Unified Technology Stack**: Single dependency for all operations within a spider.\n- ✅ **Better Error Handling**: Direct WebDriver exception management.\n- ✅ **Performance Optimization**: Reduced memory overhead.\n- ✅ **Simplified Maintenance**: One technology to debug and maintain.\n
## Data Processing Pipeline (ETL with dbt and GE)
**Extract-Load-Transform (ELT) Pattern**
```
Extract (Scrapy/Selenium) -> Raw Data
Load (PostgreSQLPipeline) -> PostgreSQL (Raw Layer) running in Docker
Validate (Great Expectations) -> Data Quality Reports
Transform (dbt) -> Staging/Dim/Fact/Agg Models
Load (dbt Materialization) -> DuckDB (Analytics Marts)
```

**Chain of Responsibility Pattern**
```python
# Pipeline execution order:
1. CrawljobPipeline (basic processing)
2. PostgreSQLPipeline (database operations - new, for PostgreSQL)
```

**Template Method Pattern (for Spiders)**
```python
# Spider workflow:
1. start_requests() -> generate URLs
2. parse_search_results() -> extract job links
3. parse_job_detail() -> extract job data
```

## 🆕 **Data Extraction Architecture**

### **Unified Extraction Strategy**
**Before**: Mixed parsing approaches (BeautifulSoup + Selenium).
**After**: Technology-specific pure implementations.

### **Standardized Error Handling Pattern**
```python
def safe_extraction_pattern():\n    \"\"\"Consistent error handling across all spiders\"\"\"\n    try:\n        # Primary extraction method\n        result = extract_primary()\n        return result or ''\n    except (NoSuchElementException, TimeoutException) as e:\n        logger.warning(f\"Primary extraction failed: {e}\")\n        try:\n            # Fallback extraction method\n            result = extract_fallback()\n            return result or ''\n        except Exception as e:\n            logger.error(f\"Fallback extraction failed: {e}\")\n            return ''\n```

### **Dynamic Content Handling Patterns**

#### **JavaScript Object Extraction**
**Pattern**: Extract data from JavaScript variables\n```python\ndef extract_js_object_data(response, js_var_name):\n    \"\"\"Extract data from JavaScript object variables\"\"\"\n    js_text = response.xpath(f'//script[contains(text(), \"{js_var_name}\")]//text()').get()\n    if js_text:\n        # Parse JavaScript object and extract data\n        return parse_js_object(js_text)\n    return None\n```\n
#### **Browser Automation Pattern**\n**Pattern**: Full browser control for complex interactions\n```python\ndef browser_automation_workflow():\n    \"\"\"Complete browser automation sequence\"\"\"\n    1. Navigate to page\n    2. Handle popups and overlays\n    3. Scroll to load content\n    4. Click interactive elements\n    5. Extract data from dynamic content\n    6. Handle pagination\n```

## Data Storage Architecture\n- **OLTP**: PostgreSQL for raw ingested data, now configured and running via Docker Compose. Scrapy pipelines (`PostgreSQLPipeline`) will load into this.
- **OLAP**: DuckDB for transformed analytics marts, populated by dbt.\n
**Repository Pattern via FastAPI**\n- PostgreSQLPipeline (new) = Repository implementation.\n- FastAPI endpoints = Repository interface.\n- Separation of data access logic.\n
**Unit of Work Pattern**\n- Database transactions per spider run (using `autocommit=True` in `psycopg2`).\n- Commit/rollback on pipeline completion.\n- Connection lifecycle management.

## API Design\n**RESTful Resource Design**\n```\nGET /health -> Service health check\nGET /jobs?keyword=X&page=Y&page_size=Z -> Job search with pagination (queries PostgreSQL)\n```

**Query Parameter Pattern**\n- Optional filtering by keyword.\n- Pagination with offset/limit.\n- Consistent response format.\n
## Web Frontend Architecture\n**Single Page Application (SPA) Pattern**\n- Vanilla JS for interactivity.\n- REST API integration.\n- Client-side rendering.\n- Progressive enhancement.\n
**Component-Based UI**\n- Reusable job card components.\n- Modular CSS classes.\n- Responsive design patterns.\n
## 🆕 **Configuration Management Evolution**\n
### **Environment-Based Configuration**\n- `.env` files for sensitive data, now including PostgreSQL connection details.
- `settings.py` for Scrapy config, now updated for PostgreSQL.
- `dbt_project.yml` for dbt configuration.\n- Airflow configurations.\n- Runtime configuration override.\n- `docker-compose.yml` for service orchestration.

### **Spider-Specific Configuration**\n**Pattern**: Technology-specific settings\n```python\n# Selenium spiders\ncustom_settings = {\n    'CONCURRENT_REQUESTS': 1,  # Single thread for browser stability\n    'DOWNLOAD_DELAY': 2,       # Rate limiting\n}\n\n# Simple Scrapy spiders\ncustom_settings = {\n    'CONCURRENT_REQUESTS': 16, # Multiple concurrent requests\n    'DOWNLOAD_DELAY': 1,       # Faster processing\n}\n```\n
## Error Handling Architecture\n**Graceful Degradation Pattern**\n- Individual spider failures do not crash the entire system.\n- Fallback parsing strategies.\n- Comprehensive logging across all components.\n
**Circuit Breaker Pattern (Implicit)**\n- Database connection retry logic.\n- Request timeout handling.\n- Selenium fallback mechanisms.\n- Airflow task retries.\n
### **New: Technology-Specific Error Handling**\n**Selenium Error Pattern**:\n```python\ndef selenium_safe_operation(operation_func):\n    \"\"\"Wrapper for Selenium operations with proper error handling\"\"\"\n    try:\n        return operation_func()\n    except (NoSuchElementException, TimeoutException) as e:\n        logger.warning(f\"Selenium operation failed: {e}\")\n        return None\n    except WebDriverException as e:\n        logger.error(f\"WebDriver error: {e}\")\n        return None\n```\n
## Scheduling Architecture\n**Apache Airflow Orchestration (New)**\n- Airflow DAGs define and schedule the entire data pipeline (`run_spiders` → `ge_validate_raw` → `dbt_run` → `publish_duckdb`).\n- Manages dependencies, retries, and alerts for all tasks.\n
**Batch Processing Pattern (Managed by Airflow)**\n- Daily execution via Airflow cron schedules.\n- Log file rotation.\n- Output file timestamping.\n
## Data Flow Architecture\n**ETL (Extract-Transform-Load) Pattern**\n```\nExtract: HTML/JavaScript -> WebDriver/Selectors -> Raw Data (Scrapy/Selenium)\nLoad: Raw Data -> PostgreSQL (Raw Layer) (PostgreSQLPipeline running in Docker)\nTransform: Raw Data -> dbt Models -> Normalized/Aggregated Data (dbt)\nLoad: Transformed Data -> DuckDB (Analytics Marts) (dbt Materialization)\n```

**Event-Driven Processing (via Airflow)**\n- Task completion in Airflow triggers dependent tasks.\n- Database operations trigger logging.\n- API requests trigger data retrieval.\n
## Security Architecture\n**Defense in Depth**\n- Environment variable protection (including PostgreSQL credentials).
- Database connection security (PostgreSQL).\n- Rate limiting for API endpoints.\n- CORS configuration.\n- **Data Quality Gates** (Great Expectations) to prevent bad data from propagating.\n
### **New: Browser Automation Security**\n- Anti-detection measures for Selenium spiders.\n- User-agent rotation and browser fingerprinting.\n- Randomized delays to mimic human behavior.\n- Cookie and session management.

## Scalability Considerations\n**Horizontal Scaling Potential**\n- Multiple spider instances.\n- Database connection pooling.\n- Concurrent request handling.\n- Distributed Airflow workers.\n
**Vertical Scaling Ready**\n- Memory optimization for large datasets.\n- Batch processing capabilities.\n- Configurable resource limits.\n
### **New: Spider-Specific Scaling**\n- Simple Scrapy: High concurrency, low resource per instance.\n- Selenium: Low concurrency, high resource per instance.\n- Technology-appropriate scaling strategies.\n
## Monitoring Architecture\n**Observer Pattern Implementation**\n- Logging observers for all components (Scrapy, Selenium, dbt, GE, Airflow, FastAPI, PostgreSQL).\n- Database operation tracking.\n- API request monitoring.\n- Spider performance metrics.\n- **Airflow UI** for overall pipeline monitoring.\n- **Great Expectations Data Docs** for data quality monitoring.\n
### **New: Technology-Specific Monitoring**\n- Selenium: Browser performance metrics, memory usage.\n- Scrapy: Request/response times, failure rates.\n- Database: Query performance, connection pooling stats.\n- dbt: Model build times, test results.\n- Airflow: DAG run status, task logs.\n
## Deployment Architecture\n**Container-Ready Design with Docker (New)**\n- All components (PostgreSQL, DuckDB, Airflow, Superset, FastAPI, Scrapy) will be containerized using Docker.\n- `docker-compose.yml` for orchestrating the multi-container application in development and potentially production.
- Dependency isolation.\n- Configuration externalization.\n- Environment-specific settings.\n
**Windows Service Pattern (Deprecated for full DE stack)**\n- Task Scheduler integration (will be replaced by Airflow).\n
---\n
**The architecture has evolved from mixed technology approaches to pure technology stacks, now integrating a modern data engineering stack, with PostgreSQL firmly established as the OLTP database via Docker Compose, to provide better consistency, performance, and maintainability while supporting advanced data transformation, quality, and analytics requirements.**