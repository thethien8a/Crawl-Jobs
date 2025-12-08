# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import logging
import psycopg2
from itemadapter import ItemAdapter
from scrapy.utils.project import get_project_settings

logger = logging.getLogger(__name__)

from scrapy.exceptions import DropItem
from pydantic import ValidationError
from .PrevStagingQuality.schema import PrevStagingQualitySchema

class ValidateItemPipeline:
    def process_item(self, item, spider):
        try:
            job_data = PrevStagingQualitySchema(**item)
            item['job_title'] = job_data.job_title
            item['company_name'] = job_data.company_name
            item['location'] = job_data.location
            item['job_description'] = job_data.job_description
            item['source_site'] = job_data.source_site
            item['job_url'] = job_data.job_url
            item['salary'] = job_data.salary
            item['job_type'] = job_data.job_type
            item['job_industry'] = job_data.job_industry
            item['experience_level'] = job_data.experience_level
            item['education_level'] = job_data.education_level
            item['job_position'] = job_data.job_position
            item['requirements'] = job_data.requirements
            item['benefits'] = job_data.benefits
            item['job_deadline'] = job_data.job_deadline
            item['search_keyword'] = job_data.search_keyword
            item['scraped_at'] = job_data.scraped_at

            return item
            
        except ValidationError as e:
            error_msg = str(e)
            spider.logger.warning(f"⚠️ Drop Item: {error_msg} | URL: {item.get('job_url', 'No URL')}")
            raise DropItem(f"Validation failed: {e}")


# PostgreSQL Pipeline với BATCH INSERT để tối ưu hiệu suất
class PostgreSQLPipeline:
    def __init__(self):
        settings = get_project_settings()
        self.conn = None
        self.cursor = None

    
        self.batch_size = settings.get("POSTGRES_BATCH_SIZE", 50)  # Số items trong 1 batch
        self.items_buffer = []  # Buffer để chứa items trước khi insert
        self.items_count = 0  # Đếm số items đã xử lý

        self.db_params = {
            "host": settings.get("POSTGRES_HOST"),
            "port": settings.get("POSTGRES_PORT"),
            "database": settings.get("POSTGRES_DB"),
            "user": settings.get("POSTGRES_USER"),
            "password": settings.get("POSTGRES_PASSWORD"),
        }

        # Thử kết nối ngay khi khởi tạo
        try:
            self.conn = psycopg2.connect(**self.db_params)
            self.conn.autocommit = False  # TẮT autocommit để sử dụng batch insert
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to PostgreSQL successfully. Batch size: {self.batch_size}")
            self._create_table_if_not_exists(self.cursor)
            self.conn.commit()  # Commit sau khi tạo bảng
        except psycopg2.Error as e:
            logger.error(f"Error connecting to PostgreSQL: {e}")
            if self.conn:
                self.conn.rollback()
            self.conn = None
            self.cursor = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def _create_table_if_not_exists(self, cursor):
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS staging_jobs (
            id SERIAL PRIMARY KEY,
            job_title VARCHAR(500) NOT NULL,
            company_name VARCHAR(500) NOT NULL,
            salary VARCHAR(500),
            location VARCHAR(500) NOT NULL,
            job_type VARCHAR(500),
            job_industry VARCHAR(500),
            experience_level VARCHAR(500),
            education_level VARCHAR(500),
            job_position VARCHAR(500),
            job_description TEXT NOT NULL,
            requirements TEXT,
            benefits TEXT,
            job_deadline VARCHAR(500),
            source_site VARCHAR(500) NOT NULL,
            job_url VARCHAR(1000) NOT NULL,
            search_keyword VARCHAR(500) NOT NULL,
            scraped_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            updated_at TIMESTAMP
        );
        """
        )

    def process_item(self, item, spider):
        """
        Thêm item vào buffer.
        Khi buffer đầy (đủ batch_size) → Flush toàn bộ buffer vào database.
        """
        if not self.conn or not self.cursor:
            logger.error("Database connection not available. Skipping item.")
            return item

        adapter = ItemAdapter(item)

        # Lấy giá trị cho các trường và lưu vào buffer
        item_data = (
            adapter.get("job_title"),
            adapter.get("company_name"),
            adapter.get("salary"),
            adapter.get("location"),
            adapter.get("job_type"),
            adapter.get("job_industry"),
            adapter.get("experience_level"),
            adapter.get("education_level"),
            adapter.get("job_position"),
            adapter.get("job_description"),
            adapter.get("requirements"),
            adapter.get("benefits"),
            adapter.get("job_deadline"),
            adapter.get("source_site"),
            adapter.get("job_url"),
            adapter.get("search_keyword"),
            adapter.get("scraped_at"),
        )

        # Thêm vào buffer
        self.items_buffer.append(item_data)
        self.items_count += 1

        # Nếu buffer đầy → Flush ngay
        if len(self.items_buffer) >= self.batch_size:
            self._flush_items()

        return item

    def _flush_items(self):
        """
        Insert tất cả items trong buffer vào database bằng 1 lần execute.
        Sau đó clear buffer.
        """
        if not self.items_buffer:
            return  # Không có gì để insert


        insert_sql = """
        INSERT INTO staging_jobs (
            job_title, company_name, salary, location, job_type, job_industry,
            experience_level, education_level, job_position, job_description,
            requirements, benefits, job_deadline, source_site, job_url,
            search_keyword, scraped_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
        )
        """
        try:
            # Sử dụng executemany để insert nhiều rows cùng lúc
            self.cursor.executemany(insert_sql, self.items_buffer)
            self.conn.commit()  
            
            logger.info(
                f"Batch inserted {len(self.items_buffer)} items successfully. "
                f"Total processed: {self.items_count}"
            )
            
            # Clear buffer sau khi insert thành công
            self.items_buffer.clear()
            
        except psycopg2.Error as e:
            logger.error(f"Error batch inserting items to PostgreSQL: {e}")
            self.conn.rollback()  # Rollback nếu có lỗi
            self.items_buffer.clear()

    def close_spider(self, spider):
        """
        Khi spider kết thúc:
        1. Flush các items còn lại trong buffer (nếu có)
        2. Đóng cursor và connection
        """
        # Flush items còn lại trong buffer
        if self.items_buffer:
            logger.info(f"Flushing {len(self.items_buffer)} remaining items before closing...")
            self._flush_items()
        
        # Đóng connection
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        
        logger.info(f"PostgreSQL connection closed. Total items processed: {self.items_count}")
