# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobItem(scrapy.Item):
    # Job basic information
    job_title = scrapy.Field()
    company_name = scrapy.Field()
    salary = scrapy.Field()
    location = scrapy.Field()

    # Job details
    job_type = scrapy.Field()  # Full-time, Part-time, etc.
    experience_level = scrapy.Field()
    education_level = scrapy.Field()
    job_industry = scrapy.Field()
    job_position = scrapy.Field()

    # Job description and requirements
    job_description = scrapy.Field()
    requirements = scrapy.Field()
    benefits = scrapy.Field()

    # Job deadline
    job_deadline = scrapy.Field()  # Hạn cuối nộp CV

    # Metadata
    source_site = scrapy.Field()
    job_url = scrapy.Field()
    search_keyword = scrapy.Field()

    # Timestamp
    scraped_at = scrapy.Field()

    # Quarantine metadata (pipeline flags + error context)
    need_quarantine = scrapy.Field()
    quarantine_error_field = scrapy.Field()
    quarantine_error_message = scrapy.Field()
    quarantine_bug_time = scrapy.Field()
    quarantine_raw_item = scrapy.Field()