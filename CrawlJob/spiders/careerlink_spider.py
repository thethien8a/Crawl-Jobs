import scrapy
from datetime import datetime, timedelta
from ..items import JobItem
from ..utils import encode_input, clean_location
import re

class CareerlinkSpider(scrapy.Spider):
    name = 'careerlink'
    allowed_domains = ['careerlink.vn']

    def __init__(self, keyword=None, *args, **kwargs):
        super(CareerlinkSpider, self).__init__(*args, **kwargs)
        self.keyword = keyword or 'data analyst'
        self._count_page = 0
        self._max_page = 3
        self._unique_job_urls = set()
        
    def start_requests(self):
        base_url = 'https://www.careerlink.vn/viec-lam'
        search_word = encode_input(self.keyword)
        search_url = f"{base_url}/k/{search_word}"

        yield scrapy.Request(
            url=search_url,
            callback=self.parse_search_results,
            meta={'keyword': self.keyword}
        )

    def parse_search_results(self, response):
        job_urls = response.css('a[class*="job-link"][href*="tim-viec-lam"]::attr(href)').getall()

        for link in job_urls:
            if link and link not in self._unique_job_urls:
                self._unique_job_urls.add(link)

        self.logger.info(f"Found {len(job_urls)} job listings")

        for job_url in job_urls:
            yield response.follow(
                job_url, 
                callback=self.parse_job_detail,
                meta=response.meta
                )

        self._count_page += 1
        # Next page
        next_page = response.css('a[href*="?page="]::attr(href)').get()
        if next_page and self._count_page < self._max_page:
            if not next_page.startswith('http'):
                next_page = f"https://www.careerlink.vn{next_page}"
            yield scrapy.Request(
                url=next_page,
                callback=self.parse_search_results,
                meta=response.meta
            )

    def parse_job_detail(self, response):
        item = JobItem()

        # Title
        title = response.css('h1#job-title::text').get()
        item['job_title'] = title.strip() if title else None

        # Company name
        company = response.css('a[href*="viec-lam-cua"] ::text').get()
        item['company_name'] = company.strip() if company else None

        # Salary
        salary = self._extract_by_icon(response, 'cli-currency-circle-dollar')
        item['salary'] = salary

        location = self._extract_by_icon(response, 'cli-map-pin-line')
        if not location:
            location = self._extract_by_icon(response, 'cli-building')
        item["location"] = location

        # Job type
        job_type = self._extract_by_text(response, 'Loại công việc')
        item['job_type'] = job_type

        # Experience level
        experience = self._extract_by_text(response, 'Kinh nghiệm')
        item['experience_level'] = experience

        # Education level
        education = self._extract_by_text(response, 'Học vấn')
        item['education_level'] = education

        # Job industry
        job_industry = self._extract_by_text_all(response, 'Ngành nghề')
        item['job_industry'] = job_industry

        # Job position
        job_position = self._extract_by_text(response, 'Cấp bậc')
        item['job_position'] = job_position

        # Job deadline
        job_deadline = response.css('div[class*="day-expired"] ::text').getall()
        if job_deadline:
            days_remaining = int(re.findall(r'\d+', job_deadline[2])[0])
            deadline_date = datetime.now().date() + timedelta(days=days_remaining)
            item['job_deadline'] = deadline_date.strftime('%Y-%m-%d')
        else:
            item['job_deadline'] = None
        
        # Job description
        description = response.css("div.rich-text-content ::text").getall()
        item['job_description'] = ' '.join([d.strip() for d in description if d.strip()])

        # Requirements
        requirements = response.css('div.raw-content.rich-text-content ::text').getall()
        item['requirements'] = ' '.join([b.strip() for b in requirements if b.strip()])

        # Benefits
        all_benefits = []
        benefit_items = response.css('div[class*="job-benefit-item"]')
        if benefit_items:
            for b_item in benefit_items:
                benefit_text = b_item.css('::text').getall()
                clean_text = ' '.join([text.strip() for text in benefit_text if text.strip()])
                if clean_text:
                    all_benefits.append(clean_text)
        final_benefits = ' '.join(all_benefits)
        item['benefits'] = final_benefits
        
        # Metadata
        item['source_site'] = 'careerlink.vn'
        item['job_url'] = response.url
        item['search_keyword'] = response.meta['keyword']
        item['scraped_at'] = datetime.now().isoformat()

        yield item

    def _extract_by_icon(self, response, icon_class):
        text = response.xpath(f"//i[contains(@class, '{icon_class}')]/following-sibling::span[1]//text()").getall()
        if text:
            return ' '.join([t.strip() for t in text])
        return None
    
    def _extract_by_text(self, response, label_text):
        text = response.xpath(f'//div[contains(text(), "{label_text}")]/following-sibling::div[1]//text()').get()
        if text:
            return text.strip()
        return None
    
    def _extract_by_text_all(self, response, label_text):
        text = response.xpath(f'//div[contains(text(), "{label_text}")]/following-sibling::div[1]//text()').getall()
        if text:
            return ' '.join([t.strip() for t in text])
        return None
    