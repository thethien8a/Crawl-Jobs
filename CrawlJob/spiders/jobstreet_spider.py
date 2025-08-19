import scrapy
from datetime import datetime
from urllib.parse import urlencode
from ..items import JobItem


class JobStreetSpider(scrapy.Spider):
    name = 'jobstreet'
    allowed_domains = ['jobstreet.vn']

    def __init__(self, keyword=None, location=None, *args, **kwargs):
        super(JobStreetSpider, self).__init__(*args, **kwargs)
        self.keyword = keyword or 'data analyst'
        self._pages_crawled = 0
        self._max_pages = 5

    def start_requests(self):
        base_url = 'https://www.jobstreet.vn/j'
        params = {
            'sp': 'search',
            'q': self.keyword,
        }
        url = f"{base_url}?{urlencode(params)}"
        yield scrapy.Request(
            url=url,
            callback=self.parse_search_results,
            meta={'keyword': self.keyword}
        )

    def parse_search_results(self, response):
        # Unique job links
        job_links = set()

        job_results_section = response.css('#jobresults')
        for href in job_results_section.css('a[class*="job-link"]::attr(href)').getall():
            if href:
                job_links.add(href)


        for href in job_links:
            yield response.follow(
                href,
                callback=self.parse_job_detail,
                meta={'keyword': response.meta.get('keyword', self.keyword)}
            )

        
        self._pages_crawled += 1
        next_href = response.css('a[class*="next-page-button"]::attr(href)').get()
        if self._pages_crawled < self._max_pages and next_href:
            yield response.follow(
                next_href,
                callback=self.parse_search_results,
                meta=response.meta
            )

    def parse_job_detail(self, response):
        item = JobItem()
        
        # Title
        title = response.css('h1[class*="job-title"]::text').get()
        item['job_title'] = (title or '').strip()
        
        # Company
        company = response.css('[class*="company"]::text').get()
        item['company_name'] = (company or '').strip()
        
        # Salary
        item['salary'] = ''
        
        # Location
        location = response.css('[class*="location"]::text').get()
        item['location'] = (location or '').strip()
        
        item['job_type'] = response.css('div.badge.-default-badge div[class*="content"]::text').get()
        
        # No have
        item['experience_level'] = ''
        item['education_level'] = ''
        item['job_industry'] = ''
        item['job_position'] = ''
        
        
        # Long texts: gộp description là của cả requirements và benefits
        item['job_description'] = ' '.join(response.css('div#job-description-container ::text').getall())
        item['requirements'] = ''
        item['benefits'] = ''
        
        # Deadline
        item['job_deadline'] = ''
        
        # Metadata
        item['source_site'] = 'jobstreet.vn'
        item['job_url'] = response.url
        item['search_keyword'] = response.meta.get('keyword', self.keyword)
        item['scraped_at'] = datetime.now().isoformat()
        return item
