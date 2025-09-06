# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import psycopg2
from itemadapter import ItemAdapter
from scrapy.utils.project import get_project_settings
import logging

logger = logging.getLogger(__name__)


class CrawljobPipeline:
    def process_item(self, item, spider):
        if not item.get('job_title'):
            return None
        return item


# PostgreSQL Pipeline (MỚI hoặc thay thế SQLServerPipeline)
class PostgreSQLPipeline:
    def __init__(self):
        settings = get_project_settings()
        self.conn = None
        self.cursor = None
        
        self.db_params = {
            'host': settings.get('POSTGRES_HOST'),
            'port': settings.get('POSTGRES_PORT'),
            'database': settings.get('POSTGRES_DB'),
            'user': settings.get('POSTGRES_USER'),
            'password': settings.get('POSTGRES_PASSWORD')
        }
        
        # Thử kết nối ngay khi khởi tạo
        try:
            self.conn = psycopg2.connect(**self.db_params)
            self.conn.autocommit = True # Set autocommit to True
            self.cursor = self.conn.cursor()
            logger.info("Connected to PostgreSQL successfully.")
            self._create_table_if_not_exists()
        except psycopg2.Error as e:
            logger.error(f"Error connecting to PostgreSQL: {e}")
            # Xử lý lỗi kết nối, có thể raise ngoại lệ hoặc dừng spider

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def _create_table_if_not_exists(self):
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS jobs (
            id SERIAL PRIMARY KEY,
            job_title VARCHAR(500),
            company_name VARCHAR(500),
            salary VARCHAR(200),
            location VARCHAR(200),
            job_type VARCHAR(100),
            job_industry VARCHAR(200),
            experience_level VARCHAR(200),
            education_level VARCHAR(200),
            job_position VARCHAR(200),
            job_description TEXT, -- Changed from NVARCHAR(MAX) to TEXT for PostgreSQL
            requirements TEXT,
            benefits TEXT,
            job_deadline VARCHAR(200),
            source_site VARCHAR(100),
            job_url VARCHAR(1000) UNIQUE, -- Changed to UNIQUE to simplify upsert logic
            search_keyword VARCHAR(200),
            scraped_at VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        );
        """
        try:
            self.cursor.execute(create_table_sql)
            # No need to commit here if autocommit is True
            logger.info("Table 'jobs' checked/created successfully.")
        except psycopg2.Error as e:
            logger.error(f"Error creating 'jobs' table: {e}")
            # self.conn.rollback() # No rollback needed with autocommit

    def process_item(self, item, spider):
        if not self.conn or not self.cursor:
            logger.error("Database connection not available. Skipping item.")
            return item

        adapter = ItemAdapter(item)
        
        # Lấy giá trị cho các trường
        job_title = adapter.get('job_title')
        company_name = adapter.get('company_name')
        salary = adapter.get('salary')
        location = adapter.get('location')
        job_type = adapter.get('job_type')
        job_industry = adapter.get('job_industry')
        experience_level = adapter.get('experience_level')
        education_level = adapter.get('education_level')
        job_position = adapter.get('job_position')
        job_description = adapter.get('job_description')
        requirements = adapter.get('requirements')
        benefits = adapter.get('benefits')
        job_deadline = adapter.get('job_deadline')
        source_site = adapter.get('source_site')
        job_url = adapter.get('job_url')
        search_keyword = adapter.get('search_keyword')
        scraped_at = adapter.get('scraped_at')

        # Logic UPSERT (INSERT ON CONFLICT DO UPDATE) cho PostgreSQL
        upsert_sql = """
        INSERT INTO jobs (
            job_title, company_name, salary, location, job_type, job_industry, 
            experience_level, education_level, job_position, job_description, 
            requirements, benefits, job_deadline, source_site, job_url, 
            search_keyword, scraped_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
        ) ON CONFLICT (job_url) DO UPDATE SET
            job_title = EXCLUDED.job_title,
            company_name = EXCLUDED.company_name,
            salary = EXCLUDED.salary,
            location = EXCLUDED.location,
            job_type = EXCLUDED.job_type,
            job_industry = EXCLUDED.job_industry,
            experience_level = EXCLUDED.experience_level,
            education_level = EXCLUDED.education_level,
            job_position = EXCLUDED.job_position,
            job_description = EXCLUDED.job_description,
            requirements = EXCLUDED.requirements,
            benefits = EXCLUDED.benefits,
            job_deadline = EXCLUDED.job_deadline,
            scraped_at = EXCLUDED.scraped_at,
            updated_at = CURRENT_TIMESTAMP;
        """
        try:
            self.cursor.execute(upsert_sql, (
                job_title, company_name, salary, location, job_type, job_industry,
                experience_level, education_level, job_position, job_description,
                requirements, benefits, job_deadline, source_site, job_url,
                search_keyword, scraped_at
            ))
            # self.conn.commit() # No commit needed if autocommit is True
            logger.info(f"Item saved/updated: {job_title} at {company_name}")
        except psycopg2.Error as e:
            logger.error(f"Error saving item to PostgreSQL: {e}")
            # self.conn.rollback() # No rollback needed with autocommit
        return item

    def close_spider(self, spider):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("PostgreSQL connection closed.")
