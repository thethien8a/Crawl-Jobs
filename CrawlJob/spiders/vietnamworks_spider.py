import scrapy
from datetime import datetime
from ..items import JobItem
from ..utils import encode_input, clean_location

class VietnamworksSpider(scrapy.Spider):
    name = 'vietnamworks'
    allowed_domains = ['vietnamworks.com']

    def __init__(self, keyword=None, *args, **kwargs):
        super(VietnamworksSpider, self).__init__(*args, **kwargs)
        self.keyword = keyword or 'data analyst'
        self._count_page = 0
        self._max_page = 5
        self._processed_urls = set()
        
    def start_requests(self):
        base_url = 'https://www.vietnamworks.com/viec-lam'
        search_url = f"{base_url}?q={self.keyword.replace(' ', '-')}"

        yield scrapy.Request(
            url=search_url,
            callback=self.parse_search_results,
            meta={'keyword': self.keyword}
        )

    def parse_search_results(self, response):
        link_urls = response.css('a[href*="source=searchResults"]::attr(href)').getall()
        self.logger.info(f"Found {len(link_urls)} job")
        
        for job_url in link_urls:
            if job_url and job_url not in self._processed_urls:
                self._processed_urls.add(job_url)
                yield response.follow(
                    url=job_url,
                    callback=self.parse_job_detail,
                    meta={
                        'keyword': response.meta['keyword'],
                    }
                )

        self._count_page += 1
        # Handle pagination
        next_page = response.css('a[href*="?page="]::attr(href)').get()
        if next_page and self._count_page < self._max_page:
            if not next_page.startswith('http'):
                next_page = f"https://www.vietnamworks.com{next_page}"
            yield scrapy.Request(
                url=next_page,
                callback=self.parse_search_results,
                meta=response.meta
            )

    def parse_job_detail(self, response):
        item = JobItem()

        # Title
        title = response.css('h1::text').get()
        item['job_title'] = title.strip() if title else ''

        # Company name
        company = response.css('.company-name::text').get()
        item['company_name'] = company.strip() if company else ''

        # Salary
        salary = response.css('.salary::text').get()
        item['salary'] = salary.strip() if salary else ''

        # Location
        location = response.css('.location::text').get()
        item['location'] = clean_location(location) if location else ''

        # Job type
        job_type = response.css('.job-type::text').get()
        item['job_type'] = job_type.strip() if job_type else ''

        # Experience level
        experience = response.css('.experience::text').get()
        item['experience_level'] = experience.strip() if experience else ''

        # Education level
        education = response.css('.education::text').get()
        item['education_level'] = education.strip() if education else ''

        # Job industry
        job_industry = response.css('.industry::text').get()
        item['job_industry'] = job_industry.strip() if job_industry else ''

        # Job position
        job_position = response.css('.position::text').get()
        item['job_position'] = job_position.strip() if job_position else ''

        # Job deadline
        job_deadline = response.css('.deadline::text').get()
        item['job_deadline'] = job_deadline.strip() if job_deadline else ''

        # Job description
        description = response.css('.job-description::text').getall()
        item['job_description'] = ' '.join([d.strip() for d in description if d.strip()])

        # Requirements
        requirements = response.css('.requirements::text').getall()
        item['requirements'] = ' '.join([r.strip() for r in requirements if r.strip()])

        # Benefits
        benefits = response.css('.benefits::text').getall()
        item['benefits'] = ' '.join([b.strip() for b in benefits if b.strip()])

        # Metadata
        item['source_site'] = 'vietnamworks.com'
        item['job_url'] = response.url
        item['search_keyword'] = response.meta['keyword']
        item['scraped_at'] = datetime.now().isoformat()

        yield item
