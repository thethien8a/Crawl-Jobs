import scrapy
import re
from datetime import datetime
from urllib.parse import urlencode
from ..items import JobItem


class TopcvSpider(scrapy.Spider):
    name = 'topcv'
    allowed_domains = ['topcv.vn']
    
    def __init__(self, keyword=None, *args, **kwargs):
        super(TopcvSpider, self).__init__(*args, **kwargs)
        self.keyword = keyword or 'python developer'  # default keyword
        
    def start_requests(self):
        """Generate search URLs based on keyword and location"""
        base_url = 'https://www.topcv.vn/'
        
        # Create search parameters
        params = {
            'keyword': self.keyword,
        }
        
        search_url = f"{base_url}?{urlencode(params)}"
        
        yield scrapy.Request(
            url=search_url,
            callback=self.parse_search_results,
            meta={'keyword': self.keyword}
        )
    
    def parse_search_results(self, response):
        """Parse the search results page"""
        # Find job listing containers - TopCV specific selectors
        job_listings = response.css('.job-item, .job-card, .job-listing, [class*="job"]')
        
        if not job_listings:
            # Try alternative selectors
            job_listings = response.css('[class*="job"], [class*="listing"], .item')
        
        self.logger.info(f"Found {len(job_listings)} job listings")
        
        for job in job_listings:
            # Extract job URL
            job_url = job.css('a::attr(href)').get()
            if job_url:
                if not job_url.startswith('http'):
                    job_url = f"https://www.topcv.vn{job_url}"
                
                yield scrapy.Request(
                    url=job_url,
                    callback=self.parse_job_detail,
                    meta={
                        'keyword': response.meta['keyword'],
                    }
                )
        
        # Handle pagination
        next_page = response.css('a[rel="next"], .pagination .next a::attr(href), .next-page a::attr(href)').get()
        if next_page:
            if not next_page.startswith('http'):
                next_page = f"https://www.topcv.vn{next_page}"
            yield scrapy.Request(
                url=next_page,
                callback=self.parse_search_results,
                meta=response.meta
            )
    
    def parse_job_detail(self, response):
        """Parse individual job detail page"""
        item = JobItem()
        
        # Basic job information - TopCV specific selectors
        item['job_title'] = self.extract_text(response, '.job-title, h1, [class*="title"]')
        item['company_name'] = self.extract_text(response, '.company-name, [class*="company"]')
        item['salary'] = self.extract_text(response, '.salary, [class*="salary"]')
        item['location'] = self.extract_text(response, '.location, [class*="location"]')
        
        # Job details
        item['job_type'] = self.extract_text(response, '.job-type, [class*="type"]')
        item['experience_level'] = self.extract_text(response, '.experience, [class*="experience"]')
        item['education_level'] = self.extract_text(response, '.education, [class*="education"]')
        
        # Job description and requirements
        item['job_description'] = self.extract_text(response, '.job-description, .description, [class*="description"]')
        item['requirements'] = self.extract_text(response, '.requirements, [class*="requirements"]')
        item['benefits'] = self.extract_text(response, '.benefits, [class*="benefits"]')
        
        # Metadata
        item['posted_date'] = self.extract_text(response, '.posted-date, [class*="date"]')
        item['source_site'] = 'topcv.vn'
        item['job_url'] = response.url
        item['search_keyword'] = response.meta['keyword']
        item['scraped_at'] = datetime.now().isoformat()
        
        # Clean and validate data
        item = self.clean_item(item)
        
        yield item
    
    def extract_text(self, response, selector):
        """Extract text from CSS selector with fallbacks"""
        text = response.css(f'{selector}::text').get()
        if not text:
            text = response.css(f'{selector}').get()
        return text.strip() if text else ''
    
    def clean_item(self, item):
        """Clean and validate item data"""
        for field, value in item.items():
            if isinstance(value, str):
                # Remove extra whitespace
                item[field] = ' '.join(value.split()) if value else ''
        return item
