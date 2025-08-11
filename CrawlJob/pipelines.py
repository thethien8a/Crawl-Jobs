# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymssql
from itemadapter import ItemAdapter
from datetime import datetime


class CrawljobPipeline:
    def process_item(self, item, spider):
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
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(create_table_sql)
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
            
            insert_sql = """
            INSERT INTO jobs (
                job_title, company_name, salary, location, job_type,
                job_industry, experience_level, education_level, job_description,
                requirements, benefits, job_deadline, source_site,
                job_url, search_keyword, scraped_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            """
            
            values = (
                item.get('job_title', ''),
                item.get('company_name', ''),
                item.get('salary', ''),
                item.get('location', ''),
                item.get('job_type', ''),
                item.get('job_industry', ''),
                item.get('experience_level', ''),
                item.get('education_level', ''),
                item.get('job_description', ''),
                item.get('requirements', ''),
                item.get('benefits', ''),
                item.get('job_deadline', ''),
                item.get('source_site', ''),
                item.get('job_url', ''),
                item.get('search_keyword', ''),
                item.get('scraped_at', '')
            )
            
            cursor.execute(insert_sql, values)
            self.connection.commit()
            cursor.close()
            
            spider.logger.info(f"Saved job: {item.get('job_title', 'Unknown')}")
            
        except Exception as e:
            spider.logger.error(f"Error saving item to database: {e}")
        
        return item
