# 📚 **STUDY PLAN: Docker Compose & dbt for CrawlJob Project**

## 🎯 **OVERVIEW**

**Duration**: 2-3 weeks  
**Focus**: Docker Compose (Advanced) + dbt (Beginner to Intermediate)  
**Goal**: Ready to implement dbt transformation layer for CrawlJob

---

## 📅 **PHASE 1: DOCKER COMPOSE ADVANCEMENT (Week 1)**

### **🎯 Objectives**
- Master multi-service Docker Compose setups
- Understand volumes, networks, and orchestration
- Create production-ready container configurations

### **📖 Learning Resources**

#### **1. Docker Compose Fundamentals (2-3 days)**
```bash
# Essential Commands
 
docker-compose down
docker-compose logs -f
docker-compose exec <service> bash
```

**Resources:**
- [Docker Compose Official Docs](https://docs.docker.com/compose/)
- [Docker Compose Best Practices](https://docs.docker.com/compose/best-practices/)
- [Real Python: Docker Compose](https://realpython.com/django-development-with-docker-compose-and-postgresql/)

#### **2. Multi-Service Orchestration (3-4 days)**
**Key Concepts:**
- Service dependencies with `depends_on`
- Environment variables management
- Volume persistence
- Network isolation
- Health checks

**Resources:**
- [Docker Compose Networking](https://docs.docker.com/compose/networking/)
- [Docker Volumes Guide](https://docs.docker.com/storage/volumes/)

### **🛠️ Hands-on Projects**

#### **Project 1: PostgreSQL + pgAdmin Setup**
```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: jobdatabase
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  pgadmin:
    image: dpage/pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@crawljob.com
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "8080:80"
    depends_on:
      postgres:
        condition: service_healthy

volumes:
  pgdata:
```

#### **Project 2: CrawlJob Database Stack**
- Create Docker Compose for PostgreSQL
- Add pgAdmin for database management
- Configure persistent volumes
- Test data persistence across container restarts

### **✅ Checkpoint 1**
- [ ] Docker Compose file with PostgreSQL + pgAdmin
- [ ] Persistent data volumes configured
- [ ] Health checks implemented
- [ ] Environment variables properly managed
- [ ] Networks and dependencies working

---

## 📅 **PHASE 2: DBT FOUNDATIONS (Week 1-2)**

### **🎯 Objectives**
- Understand dbt core concepts
- Set up dbt project structure
- Create basic transformations
- Connect to PostgreSQL database

### **📖 Learning Resources**

#### **1. dbt Fundamentals (3-4 days)**
**Key Concepts:**
- dbt project structure
- Models, sources, seeds
- Materializations
- Testing and documentation

**Resources:**
- [dbt Official Documentation](https://docs.getdbt.com/)
- [dbt Learn Courses](https://courses.getdbt.com/)
- [dbt Tutorial for Beginners](https://www.youtube.com/watch?v=4e6QDTUkYPw)

#### **2. SQL Transformations (3-4 days)**
**Key Concepts:**
- Jinja templating
- Incremental models
- CTEs and window functions
- Data quality tests

**Resources:**
- [dbt SQL Best Practices](https://docs.getdbt.com/best-practices/writing-code/sql-style-guide)
- [Jinja Template Documentation](https://jinja.palletsprojects.com/)

### **🛠️ Hands-on Projects**

#### **Project 3: dbt Project Setup**
```bash
# Initialize dbt project
dbt init crawljob_dbt

# Project structure
crawljob_dbt/
├── dbt_project.yml
├── models/
│   ├── staging/
│   ├── marts/
│   └── intermediate/
├── seeds/
├── tests/
├── macros/
└── snapshots/
```

#### **Project 4: Basic Transformations**
```sql
-- models/staging/stg_jobs.sql
WITH source AS (
    SELECT * FROM {{ source('crawljob', 'jobs') }}
)

SELECT
    id,
    job_title,
    company_name,
    location,
    salary,
    job_type,
    experience_level,
    posted_date,
    source_site,
    scraped_at
FROM source
WHERE job_title IS NOT NULL
```

#### **Project 5: PostgreSQL Connection**
```yaml
# profiles.yml
crawljob:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      port: 5432
      user: postgres
      password: password
      dbname: jobdatabase
      schema: public
```

### **✅ Checkpoint 2**
- [ ] dbt project initialized successfully
- [ ] Connected to PostgreSQL database
- [ ] Basic staging models created
- [ ] dbt run/test working
- [ ] Documentation generated

---

## 📅 **PHASE 3: INTEGRATION & ADVANCED TOPICS (Week 2-3)**

### **🎯 Objectives**
- Integrate Docker + dbt
- Create complete data models
- Implement testing and documentation
- Prepare for production deployment

### **📖 Learning Resources**

#### **3. Advanced dbt (2-3 days)**
**Key Concepts:**
- Macros and packages
- Seeds and snapshots
- Exposures and documentation
- Performance optimization

**Resources:**
- [dbt Packages](https://docs.getdbt.com/docs/build/packages)
- [dbt Exposures](https://docs.getdbt.com/docs/build/exposures)

### **🛠️ Hands-on Projects**

#### **Project 6: Docker + dbt Integration**
```yaml
# docker-compose.yml with dbt service
version: '3.8'
services:
  postgres:
    # ... existing config

  dbt:
    image: python:3.11-slim
    working_dir: /app
    volumes:
      - ./crawljob_dbt:/app
      - ~/.dbt:/root/.dbt
    command: tail -f /dev/null
    depends_on:
      postgres:
        condition: service_healthy
```

#### **Project 7: Complete Data Models**
```sql
-- models/marts/dim_companies.sql
SELECT
    ROW_NUMBER() OVER (ORDER BY company_name) as company_id,
    company_name,
    COUNT(*) as total_jobs,
    AVG(salary_min) as avg_salary_min,
    AVG(salary_max) as avg_salary_max
FROM {{ ref('stg_jobs') }}
GROUP BY company_name
```

#### **Project 8: Testing & Documentation**
```yaml
# tests/test_job_title_not_null.sql
SELECT *
FROM {{ ref('stg_jobs') }}
WHERE job_title IS NULL
```

### **✅ Checkpoint 3**
- [ ] Docker Compose with dbt service
- [ ] Complete staging models
- [ ] Dimension and fact tables
- [ ] Tests implemented
- [ ] Documentation generated

---

## 📅 **PHASE 4: CRAWLJOB INTEGRATION (Week 3)**

### **🎯 Objectives**
- Apply learning to CrawlJob project
- Create job data models
- Set up development environment
- Prepare for next technologies

### **🛠️ CrawlJob-Specific Projects**

#### **Project 9: Job Data Models**
- Staging layer for raw job data
- Dimension tables (companies, locations, industries)
- Fact tables for job postings
- Aggregate models for analytics

#### **Project 10: Development Environment**
```yaml
# Complete docker-compose.yml for CrawlJob
version: '3.8'
services:
  postgres:
    # Database
  pgadmin:
    # Database management
  dbt:
    # Data transformation
  # Future: airflow, superset, etc.
```

### **✅ Final Checkpoint**
- [ ] CrawlJob dbt models working
- [ ] Data transformations running
- [ ] Docker environment stable
- [ ] Ready for next technologies

---

## 📊 **PROGRESS TRACKING**

### **Daily Schedule**
- **Morning**: Theory & Documentation (2-3 hours)
- **Afternoon**: Hands-on Practice (3-4 hours)
- **Evening**: Project Application (1-2 hours)

### **Weekly Milestones**
- **Week 1**: Docker Compose mastery + dbt basics
- **Week 2**: dbt intermediate + integration
- **Week 3**: CrawlJob application + advanced topics

### **Learning Metrics**
- [ ] Docker Compose: Multi-service orchestration
- [ ] dbt: Project setup & basic models
- [ ] SQL: Advanced transformations
- [ ] Integration: Docker + dbt + PostgreSQL

---

## 🎯 **SUCCESS CRITERIA**

### **Technical Skills**
- [ ] Docker Compose: Production-ready multi-service setups
- [ ] dbt: Complete project with models, tests, docs
- [ ] PostgreSQL: Advanced SQL queries & optimization
- [ ] Integration: Seamless Docker + dbt workflow

### **Project Application**
- [ ] CrawlJob: dbt models for job data
- [ ] Database: Optimized PostgreSQL setup
- [ ] Documentation: Complete dbt docs
- [ ] Testing: Comprehensive test suite

### **Next Steps Ready**
- [ ] Great Expectations foundation
- [ ] Apache Airflow concepts
- [ ] DuckDB basics
- [ ] Apache Superset introduction

---

## 🚀 **RESOURCES & SUPPORT**

### **Documentation**
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [dbt Docs](https://docs.getdbt.com/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

### **Communities**
- [Docker Community](https://forums.docker.com/)
- [dbt Slack Community](https://www.getdbt.com/community/)
- [Stack Overflow](https://stackoverflow.com/)

### **Practice Platforms**
- [dbt Learn](https://courses.getdbt.com/)
- [Docker Playground](https://labs.play-with-docker.com/)
- [PostgreSQL Exercises](https://pgexercises.com/)

---

## 🎉 **FINAL GOAL**

**By end of Week 3, you will have:**
- ✅ Production-ready Docker Compose setup
- ✅ Complete dbt project with job data models
- ✅ Integrated development environment
- ✅ Ready to implement full data engineering stack
- ✅ Strong foundation for advanced technologies

**CrawlJob will have its first professional data transformation layer!** 🚀
