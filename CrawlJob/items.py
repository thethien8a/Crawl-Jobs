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
    
    # Job description and requirements
    job_description = scrapy.Field()
    requirements = scrapy.Field()
    benefits = scrapy.Field()
    
    # Metadata
    posted_date = scrapy.Field()
    source_site = scrapy.Field()
    job_url = scrapy.Field()
    search_keyword = scrapy.Field()
    
    # Timestamp
    scraped_at = scrapy.Field()
