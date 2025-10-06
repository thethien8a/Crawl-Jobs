# 📚 CrawlJob Documentation Index

Welcome to the CrawlJob documentation! This index helps you navigate through all available documentation.

---

## 🏗️ **Architecture & Design**

### **Data Warehouse**
- 📐 **[Data Warehouse Architecture](plan/DATA_WAREHOUSE_ARCHITECTURE.md)**
  - Complete guide to Bronze-Silver-Gold architecture
  - Star Schema design with Fact and Dimension tables
  - Query patterns and analytical use cases
  - Performance optimization strategies
  - dbt implementation details

- 📊 **[SCD (Slowly Changing Dimensions) Guide](learning/data-warehouse-scd-guide.md)**
  - Comprehensive guide to SCD Types 0-6
  - When to use each SCD type
  - Real-world examples from CrawlJob
  - dbt implementation patterns
  - Testing strategies

### **Overall Stack**
- 🚀 **[Data Engineering Stack Plan](plan/DATA_ENGINEERING_STACK_PLAN.md)**
  - Overall architecture overview
  - Technology stack decisions
  - Implementation roadmap
  - Component integration

---

## 📖 **Learning Resources**

### **dbt (Data Build Tool)**
- 🔨 **[dbt Introduction](learning/dbt-introduction.md)**
  - What is dbt and why use it
  - Core concepts and workflows
  - Project structure

- 📝 **[dbt Testing Guide](learning/dbt-testing-guide.md)**
  - Built-in tests (unique, not_null, etc.)
  - Custom tests
  - Data quality patterns
  - Best practices

- 🎯 **[dbt Profiles and DAG](learning/dbt-profiles-and-dag.md)**
  - Profile configuration
  - DAG dependencies
  - Model lineage

- 🗣️ **[dbt SQL Dialect](learning/dbt-sql-dialect.md)**
  - DuckDB-specific SQL
  - Jinja templating
  - Macros and functions

### **DuckDB**
- 🦆 **[DuckDB Guideline](learning/duckdb-guideline.md)**
  - What is DuckDB
  - Setup and configuration
  - SQL features
  - Integration with Python
  - Performance tips

### **Web Scraping**
- 🕷️ **[ITViec Spider Fix Guide](learning/itviec-spider-fix-stale-element.md)**
  - Selenium StaleElementReferenceException
  - Cloudflare bypass techniques
  - Retry strategies
  - Best practices for robust spiders

- 🌐 **[Chrome Version Auto-Detection](learning/chrome-version-auto-detection.md)**
  - ChromeDriver compatibility
  - Automatic version detection
  - Setup on different OS

---

## 🎯 **Quick Start Guides**

### **For New Developers**
1. Read **[Data Engineering Stack Plan](plan/DATA_ENGINEERING_STACK_PLAN.md)** for overview
2. Review **[Data Warehouse Architecture](plan/DATA_WAREHOUSE_ARCHITECTURE.md)** to understand data model
3. Check **[dbt Introduction](learning/dbt-introduction.md)** for transformation workflow

### **For Data Analysts**
1. Start with **[Data Warehouse Architecture](plan/DATA_WAREHOUSE_ARCHITECTURE.md)** - See "Analytical Use Cases" section
2. Learn about dimensions in **[SCD Guide](learning/data-warehouse-scd-guide.md)**
3. Understand **[dbt Testing Guide](learning/dbt-testing-guide.md)** for data quality

### **For Data Engineers**
1. Full stack overview: **[Data Engineering Stack Plan](plan/DATA_ENGINEERING_STACK_PLAN.md)**
2. Deep dive into warehouse: **[Data Warehouse Architecture](plan/DATA_WAREHOUSE_ARCHITECTURE.md)**
3. Master SCDs: **[SCD Guide](learning/data-warehouse-scd-guide.md)**
4. dbt best practices: **[dbt Testing Guide](learning/dbt-testing-guide.md)**

---

## 📊 **Data Model Quick Reference**

### **Bronze Layer** (Raw Data)
```
bronze.jobs - Exact replica from PostgreSQL
```

### **Silver Layer** (Cleaned & Normalized)
```
silver.stg_jobs - Cleaned, validated, normalized jobs
```

### **Gold Layer** (Analytics-Ready)

**Fact Tables:**
- `fct_jobs` - Core job postings fact
- `fct_job_skills` - Job-skill bridge table
- `fct_daily_job_stats` - Pre-aggregated daily metrics

**Dimension Tables:**
- `dim_company` (SCD Type 2) - Company master with history
- `dim_location` - Hierarchical location (City → Region)
- `dim_industry` - Industry classification
- `dim_job_category` - Job titles and seniority levels
- `dim_skill` (SCD Type 3) - Skills with trend tracking
- `dim_source_site` - Job board metadata
- `dim_date` - Standard date dimension

---

## 🔧 **Technical Stack**

| Component | Technology | Documentation |
|-----------|-----------|---------------|
| **Scraping** | Scrapy, Selenium | [Spider Fix Guide](learning/itviec-spider-fix-stale-element.md) |
| **OLTP Database** | PostgreSQL | [Stack Plan](plan/DATA_ENGINEERING_STACK_PLAN.md) |
| **OLAP Database** | DuckDB | [DuckDB Guideline](learning/duckdb-guideline.md) |
| **Orchestration** | Apache Airflow | [Stack Plan](plan/DATA_ENGINEERING_STACK_PLAN.md) |
| **Transformation** | dbt-duckdb | [dbt Introduction](learning/dbt-introduction.md) |
| **Data Quality** | Soda Core, dbt tests | [dbt Testing Guide](learning/dbt-testing-guide.md) |
| **API** | FastAPI | [Stack Plan](plan/DATA_ENGINEERING_STACK_PLAN.md) |
| **BI** | Apache Superset | [Stack Plan](plan/DATA_ENGINEERING_STACK_PLAN.md) |

---

## 🎓 **Learning Path**

### **Beginner → Intermediate**
1. ✅ Understand the overall architecture
2. ✅ Learn Bronze-Silver-Gold pattern
3. ✅ Master basic dbt models
4. ✅ Understand Star Schema basics

### **Intermediate → Advanced**
1. ✅ Deep dive into SCD patterns
2. ✅ Advanced dbt (macros, tests, snapshots)
3. ✅ Performance optimization
4. ✅ Complex analytical queries

### **Advanced → Expert**
1. ✅ Custom dbt packages
2. ✅ Advanced data quality frameworks
3. ✅ Pipeline orchestration patterns
4. ✅ Real-time processing integration

---

## 📝 **Contributing to Documentation**

When adding new documentation:
1. Place in appropriate folder (`plan/` or `learning/`)
2. Use clear, descriptive filenames (kebab-case)
3. Include table of contents for long documents
4. Add examples and code snippets
5. Update this index file
6. Cross-reference related documents

### **Documentation Standards**
- **Format**: Markdown (`.md`)
- **Diagrams**: Mermaid or ASCII
- **Code**: Use proper syntax highlighting
- **Structure**: Clear headings and sections
- **Examples**: Real examples from CrawlJob

---

## 🔗 **External Resources**

- **Kimball Group**: [Data Warehouse Toolkit](https://www.kimballgroup.com/)
- **dbt**: [Official Documentation](https://docs.getdbt.com/)
- **DuckDB**: [Official Documentation](https://duckdb.org/docs/)
- **Scrapy**: [Official Documentation](https://docs.scrapy.org/)
- **Airflow**: [Official Documentation](https://airflow.apache.org/docs/)

---

## 📞 **Need Help?**

- **Architecture Questions**: See [Data Warehouse Architecture](plan/DATA_WAREHOUSE_ARCHITECTURE.md)
- **SCD Issues**: Check [SCD Guide](learning/data-warehouse-scd-guide.md)
- **dbt Problems**: Review [dbt Testing Guide](learning/dbt-testing-guide.md)
- **Scraping Issues**: Read [Spider Fix Guide](learning/itviec-spider-fix-stale-element.md)

---

**Last Updated**: October 5, 2025  
**Maintainer**: CrawlJob Team  
**Version**: 1.0
