**BUSINESS CONTEXT AND DOMAIN KNOWLEDGE**

**Core Business Problem:**
- Aggregating and analyzing job market data from 10+ Vietnamese job sites to provide insights for job seekers, employers, and market analysts.
- Enabling data-driven decisions in recruitment, career planning, and market research.

**Target Audience/User Personas:**
1. **Job Seekers**: IT professionals, fresh graduates, career changers looking for opportunities in Vietnam.
2. **Employers/Recruiters**: Companies seeking talent acquisition insights and market analysis.
3. **Market Analysts**: Researchers studying employment trends, salary distributions, and industry growth.
4. **Data Scientists**: Users requiring clean, structured data for machine learning and predictive analytics.

**Key Business Workflows:**
1. **Data Collection**: Daily crawling of 10 job sites with keyword-based searches.
2. **Quality Assurance**: Sequential validation (schema, source-specific, coverage) to ensure data reliability.
3. **Data Processing**: Bronze-Silver-Gold transformation pipeline in DuckDB.
4. **Analytics & Reporting**: Superset dashboards for trend analysis, salary insights, and market monitoring.
5. **API Serving**: FastAPI endpoints for real-time job search and filtering.

**Domain-Specific Glossary:**
- **Job Sites**: TopCV, CareerLink, CareerViet, ITviec, 123Job, JobOKO, JobsGo, JobStreet, LinkedIn, VietnamWorks
- **Job Categories**: IT, Engineering, Marketing, Sales, Finance, Healthcare, Education
- **Salary Ranges**: Junior (< 15M VND), Mid (15-30M VND), Senior (30-50M VND), Executive (>50M VND)
- **Experience Levels**: Entry Level, Junior, Senior, Lead, Manager, Director
- **Industries**: Technology, Finance, Healthcare, Education, Manufacturing, Retail, Services
- **Data Freshness**: Real-time scraping with daily updates for trend analysis

**Business Metrics:**
- **Data Volume**: 10,000+ job listings processed daily
- **Data Quality**: 95%+ schema compliance, 100% spider coverage
- **Processing Time**: <2 hours for full pipeline (crawl → bronze → silver → gold)
- **API Performance**: <500ms response time for job queries
- **User Engagement**: Dashboard views, API calls, data export requests

**Competitive Landscape:**
- **Similar Tools**: VietnamWorks, TopCV internal analytics, LinkedIn Talent Insights
- **Differentiators**: Multi-site aggregation, real-time quality validation, open analytics layer
- **Market Position**: Free alternative to paid job market analytics tools

**Regulatory Considerations:**
- **Data Privacy**: Respect robots.txt, avoid personal data extraction
- **Copyright**: Aggregate public job data without reproducing copyrighted content
- **Compliance**: GDPR considerations for EU users, local data laws in Vietnam

**Monetization Opportunities:**
- **Premium Analytics**: Advanced trend reports, salary predictions, market forecasts
- **API Access**: Paid tiers for high-volume data access
- **Custom Dashboards**: Tailored analytics for enterprise clients
- **Data Products**: Clean datasets for ML training and research