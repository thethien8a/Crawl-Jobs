import scrapy
from datetime import datetime
from urllib.parse import urljoin, quote
import re
from ..items import JobItem
from ..utils import encode_input


class Job123Spider(scrapy.Spider):
    name = '123job'
    allowed_domains = ['123job.vn']

    def __init__(self, keyword=None, *args, **kwargs):
        super(Job123Spider, self).__init__(*args, **kwargs)
        self.keyword = keyword or 'data analyst'
        self._pages_crawled = 0
        self._max_pages = 5

    def start_requests(self):
        base_url = 'https://123job.vn/tuyen-dung'
        encoded_keyword = quote(self.keyword)
        search_url = f"{base_url}?q={encoded_keyword}"
        
        yield scrapy.Request(
            url=search_url,
            callback=self.parse_search_results,
            meta={'keyword': self.keyword}
        )

    def parse_search_results(self, response):
        job_links = response.css('a[href*="/viec-lam/"]::attr(href)').getall()
        seen = set()
        for href in job_links:
            if not href:
                continue
            if href in seen:
                continue
            seen.add(href)
            yield response.follow(
                href,
                callback=self.parse_job_detail,
                meta={'keyword': response.meta.get('keyword', self.keyword)}
            )

        self._pages_crawled += 1
        # Phân trang (nếu có)
        next_page = response.css('a[rel="Next"]::attr(href)').get()
        if next_page and self._pages_crawled < self._max_pages:
            yield scrapy.Request(
                next_page,
                callback=self.parse_search_results,
                meta=response.meta
            )

    def parse_job_detail(self, response):
        item = JobItem()

        # Tiêu đề
        item['job_title'] = self._parse_text_in_class(response, 'job-title')

        # Công ty
        item['company_name'] = self._parse_text_in_class(response, 'company-name')

        # Lương / Thu nhập
        item['salary'] = self._parse_text_in_follow_sibling(response, 'Mức lương')

        # Địa điểm
        item['location'] = self._parse_text_in_follow_sibling(response, 'Địa điểm làm việc')

        # Chi tiết
        item['job_type'] = self._parse_text_in_follow_sibling(response, 'Hình thức làm việc')
        
        item['experience_level'] = self._parse_text_in_follow_sibling(response, 'Kinh nghiệm yêu cầu')
        
        item['education_level'] = self._parse_text_in_follow_sibling(response, 'Trình độ yêu cầu')
        
        item['job_industry'] = self._parse_text_in_follow_sibling(response, 'Ngành nghề')
        
        item['job_position'] = self._parse_text_in_follow_sibling(response, 'Cấp bậc')
        
        # Nội dung mô tả, yêu cầu, quyền lợi
        item['job_description'] = self._parse_paragraph_in_follow_sibling(response, 'Mô tả công việc')
        item['requirements'] = self._parse_paragraph_in_follow_sibling(response, 'Yêu cầu')
        item['benefits'] = self._parse_paragraph_in_follow_sibling(response, 'Quyền lợi')

        # Hạn nộp
        item['job_deadline'] = self._parse_text_in_follow_sibling(response, 'Hạn nộp')

        # Metadata
        item['source_site'] = '123job.vn'
        item['job_url'] = response.url
        item['search_keyword'] = response.meta.get('keyword', self.keyword)
        item['scraped_at'] = datetime.now().isoformat()

        return item

    def _parse_text_in_class(self, reponse, class_name):
        text = reponse.css(f"[class*='{class_name}'] ::text").get()
        if text:
            return text.strip()
        return ''
    
    def _parse_text_in_follow_sibling(self, response, text_extract):
        text = response.xpath(f"//*[contains(text(), '{text_extract}')]/following-sibling::*[1]/text()").get()
        if text:
            return text.strip()
        return ''
    
    def _parse_paragraph_in_follow_sibling(self, response, text_extract):
        para = response.xpath(f'//h2[contains(normalize-space(.), "{text_extract}")]/following-sibling::*[1]//text()').getall()
        if para:
            return ' '.join(para)
        return ''
    