import scrapy
import re
from datetime import datetime
from urllib.parse import urljoin, quote
from ..items import JobItem
from ..utils import clean_text_with_tab

class CareervietSpider(scrapy.Spider):
    name = 'careerviet'
    allowed_domains = ['careerviet.vn']

    def __init__(self, keyword=None, *args, **kwargs):
        super(CareervietSpider, self).__init__(*args, **kwargs)
        self.keyword = keyword or 'data analyst'
        self._pages_crawled = 0
        self._max_pages = 5

    def start_requests(self):
        base_url = 'https://careerviet.vn/'
        search_url = urljoin(base_url, f'viec-lam/{quote(self.keyword.replace(" ", "-"))}-k-vi.html')
        
        yield scrapy.Request(
            url=search_url,
            callback=self.parse_search_results,
            meta={'keyword': self.keyword}
        )

    def parse_search_results(self, response):
        # Collect job detail links
        job_links = set()
        
        for href in response.css('a[href*="/tim-viec-lam/"]::attr(href)').getall():
            if href:
                job_links.add(href)
        
        for href in job_links:
            yield response.follow(
                href,
                callback=self.parse_job_detail,
                meta={'keyword': response.meta.get('keyword', self.keyword)}
            )

        # Next page
        self._pages_crawled += 1
        next_page = response.css('a[class*="next-page"]::attr(href)').get()
        if next_page and self._pages_crawled < self._max_pages:
            yield response.follow(
                next_page,
                callback=self.parse_search_results,
                meta=response.meta
            )

    def parse_job_detail(self, response):
        item = JobItem()

        # Title
        item['job_title'] = response.css('h1.title::text').get()

        # Company
        item['company_name'] = response.css('a.employer.job-company-name::text').get()

        # Salary
        item['salary'] = self._extract_detail_text(response, "Lương")
        
        # Location
        item['location'] = self._extract_detail_text(response, 'Địa điểm')

        # Details
        item['job_type'] = self._extract_detail_text(response, 'Hình thức')
        item['experience_level'] = ' '.join(self._extract_detail_text(response, 'Kinh nghiệm').split())
        
        # Education level
        item['education_level'] = ''
        for text in response.css('div.content_fck li::text').getall():
            if "Bằng cấp" in text:
                item['education_level'] = clean_text_with_tab(' '.join(text.split()))
                break
        
        item['job_industry'] = self._extract_detail_text(response, 'Ngành nghề')
        item['job_position'] = self._extract_detail_text(response, 'Cấp bậc')

        # Long texts
        item['job_description'] = self._extract_detail_paragraph(response, 'Mô tả Công việc')
        item['requirements'] = self._extract_detail_paragraph(response, 'Yêu Cầu Công Việc')
        item['benefits'] = self._extract_detail_paragraph(response, 'Phúc lợi')

        # Deadline
        item['job_deadline'] = self._extract_detail_text(response, 'Hết hạn nộp')

        # Metadata
        item['source_site'] = 'careerviet.vn'
        item['job_url'] = response.url
        item['search_keyword'] = response.meta.get('keyword', self.keyword)
        item['scraped_at'] = datetime.now().isoformat()

        return item

    def _extract_detail_text(self, response, text_extract):
        value = response.xpath(f'//strong[contains(normalize-space(.), "{text_extract}")]/following-sibling::p//text()').getall()
        if value:
            return clean_text_with_tab(' '.join(value).strip())
        return ''
    
    def _extract_detail_paragraph(self, response, text_extract):
        texts = response.xpath(f'//h2[contains(normalize-space(.), "{text_extract}")]/following-sibling::*//text()').getall()
        if texts:
            return (' '.join(clean_text_with_tab(text) for text in texts))
        return ''

    