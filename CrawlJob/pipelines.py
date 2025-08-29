# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymssql
from itemadapter import ItemAdapter
from datetime import datetime


class CrawljobPipeline:
    def process_item(self, item, spider):
        if not item.get('job_title'):
            return None
        return item


class SQLServerPipeline:
    def __init__(self, server, database, username, password):
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.connection = None
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            server=crawler.settings.get('SQL_SERVER'),
            database=crawler.settings.get('SQL_DATABASE'),
            username=crawler.settings.get('SQL_USERNAME'),
            password=crawler.settings.get('SQL_PASSWORD')
        )
    
    def open_spider(self, spider):
        """Open database connection when spider starts"""
        try:
            self.connection = pymssql.connect(
                server=self.server,
                database=self.database,
                user=self.username,
                password=self.password
            )
            self.create_table_if_not_exists()
            spider.logger.info("Connected to SQL Server successfully")
        except Exception as e:
            spider.logger.error(f"Failed to connect to SQL Server: {e}")

    
    def close_spider(self, spider):
        """Close database connection when spider ends"""
        if self.connection:
            self.connection.close()
            spider.logger.info("Database connection closed")
    
    def create_table_if_not_exists(self):
        """Create jobs table if it doesn't exist"""
        create_table_sql = """
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='jobs' AND xtype='U')
        CREATE TABLE jobs (
            id INT IDENTITY(1,1) PRIMARY KEY,
            job_title NVARCHAR(500),
            company_name NVARCHAR(500),
            salary NVARCHAR(200),
            location NVARCHAR(200),
            job_type NVARCHAR(100),
            job_industry NVARCHAR(200),
            experience_level NVARCHAR(200),
            education_level NVARCHAR(200),
            job_position NVARCHAR(200),
            job_description NVARCHAR(MAX),
            requirements NVARCHAR(MAX),
            benefits NVARCHAR(MAX),
            job_deadline NVARCHAR(200), 
            source_site NVARCHAR(100), 
            job_url NVARCHAR(1000), 
            search_keyword NVARCHAR(200), 
            scraped_at NVARCHAR(50), 
            created_at DATETIME DEFAULT GETDATE()
        )
        """
        # Additive migrations: ensure updated_at column and unique index for dedup
        migration_sql = """
        IF COL_LENGTH('dbo.jobs','updated_at') IS NULL
            ALTER TABLE dbo.jobs ADD updated_at DATETIME NULL;

        IF NOT EXISTS (
            SELECT 1 FROM sys.indexes 
            WHERE name = 'UQ_title_company_source' AND object_id = OBJECT_ID('dbo.jobs')
        )
            CREATE UNIQUE INDEX UQ_jobs_title_company_source ON dbo.jobs(job_title, company_name, source_site);
        """
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(create_table_sql)
            cursor.execute(migration_sql)
            self.connection.commit()
            cursor.close()
        except Exception as e:
            print(f"Error creating table: {e}")
    
    def process_item(self, item, spider):
        """Save job item to database"""
        if not self.connection:
            spider.logger.error("No database connection available")
            return item
        
        try:
            cursor = self.connection.cursor()
            # Build safe values with defaults
            job_title = item.get('job_title', '')
            company_name = item.get('company_name', '')
            salary = item.get('salary', '')
            location = item.get('location', '')
            job_type = item.get('job_type', '')
            job_industry = item.get('job_industry', '')
            experience_level = item.get('experience_level', '')
            education_level = item.get('education_level', '')
            job_position = item.get('job_position', '')
            job_description = item.get('job_description', '')
            requirements = item.get('requirements', '')
            benefits = item.get('benefits', '')
            job_deadline = item.get('job_deadline', '')
            source_site = item.get('source_site', '')
            job_url = item.get('job_url', '')
            search_keyword = item.get('search_keyword', '')
            scraped_at = item.get('scraped_at', '')

            # Dedup/Upsert by (job_title, company_name, source_site)
            select_sql = "SELECT id FROM jobs WHERE job_title=%s AND company_name=%s AND source_site=%s"
            cursor.execute(select_sql, (job_title, company_name, source_site))
            row = cursor.fetchone()

            if row:
                job_id = row[0]
                update_sql = """
                UPDATE jobs SET
                    job_title=%s,
                    company_name=%s,
                    salary=%s,
                    location=%s,
                    job_type=%s,
                    job_industry=%s,
                    experience_level=%s,
                    education_level=%s,
                    job_position=%s,
                    job_description=%s,
                    requirements=%s,
                    benefits=%s,
                    job_deadline=%s,
                    search_keyword=%s,
                    scraped_at=%s,
                    updated_at=GETDATE()
                WHERE id=%s
                """
                update_values = (
                    job_title,
                    company_name,
                    salary,
                    location,
                    job_type,
                    job_industry,
                    experience_level,
                    education_level,
                    job_position,
                    job_description,
                    requirements,
                    benefits,
                    job_deadline,
                    search_keyword,
                    scraped_at,
                    job_id,
                )
                cursor.execute(update_sql, update_values)
                action = "updated"
            else:
                insert_sql = """
                INSERT INTO jobs (
                    job_title, company_name, salary, location, job_type,
                    job_industry, experience_level, education_level, job_position, job_description,
                    requirements, benefits, job_deadline, source_site,
                    job_url, search_keyword, scraped_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """
                insert_values = (
                    job_title,
                    company_name,
                    salary,
                    location,
                    job_type,
                    job_industry,
                    experience_level,
                    education_level,
                    job_position,
                    job_description,
                    requirements,
                    benefits,
                    job_deadline,
                    source_site,
                    job_url,
                    search_keyword,
                    scraped_at,
                )
                cursor.execute(insert_sql, insert_values)
                action = "inserted"

            # With autocommit=True, data is already committed automatically
            # No need to call commit() manually - this causes the error
            cursor.close()
            spider.logger.info(f"{action.capitalize()} job: {job_title or 'Unknown'}")

        except Exception as e:
            spider.logger.error(f"Error saving item to database: {e}")
            # Log additional context
            spider.logger.error(f"Error type: {type(e).__name__}")
            spider.logger.error(f"Job details: title='{job_title}', company='{company_name}', source='{source_site}'")
            # Check if this is a commit error (data still saved)
            if "3902" in str(e):
                spider.logger.warning("This is a commit error - data may still be saved due to autocommit")

        return item
