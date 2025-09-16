import scrapy
import json
from datetime import datetime
from ..items import JobItem
from ..utils import encode_input



class TopcvSpider(scrapy.Spider):
    name = 'topcv'
    allowed_domains = ['topcv.vn']

    def __init__(self, keyword=None, *args, **kwargs):
        super(TopcvSpider, self).__init__(*args, **kwargs)
        self.keyword = keyword or 'data analyst'
        self._count_page = 0
        self._max_page = 3
        self.unique_job_urls = set()
        
    def start_requests(self):
        base_url = 'https://www.topcv.vn/tim-viec-lam'
        search_word = encode_input(self.keyword)
        search_url = f"{base_url}-{search_word}"

        yield scrapy.Request(
            url=search_url,
            callback=self.parse_search_results,
            meta={'keyword': self.keyword}
        )

    def parse_search_results(self, response):
        job_urls = response.css('a[href*="/viec-lam/"]::attr(href), a[href*="/brand/"][href*="tuyen-dung"]::attr(href)').getall()
        self.logger.info(f"Found {len(job_urls)} job listings")
    
        for job_url in job_urls:
            if job_url not in self.unique_job_urls:
                self.unique_job_urls.add(job_url)
                yield scrapy.Request(
                    url=job_url,
                    callback=self.parse_job_detail,
                    meta={
                        'keyword': response.meta['keyword'],
                    }
                )

        self._count_page += 1
        # Handle pagination
        next_page = response.css('a[data-href*="?page="]::attr(data-href)').get()
        if next_page and self._count_page < self._max_page:
            yield scrapy.Request(
                url=next_page,
                callback=self.parse_search_results,
                meta=response.meta
            )

    def parse_job_detail(self, response):
        item = JobItem()

        # Title
        if 'brand' in response.url:
            title = response.css('h2[class="premium-job-basic-information__content--title"] ::text').getall()
            if not title:
                title = response.css('h2[class*="title"] ::text').getall()
            item['job_title'] = ' '.join([t.strip() for t in title if t.strip()])         
        else:
            # Job title - Extract from JavaScript object first
            title = self._extract_from_js_object(response, 'job_title')
            if not title:
                # Fallback: HTML extraction
                title_element = response.css('h1.box-header-job__title')
                if title_element:
                    title_texts = title_element.css('::text').getall()
                    title = [t.strip() for t in title_texts if t.strip()]
                    title = ' '.join(title)
            item['job_title'] = title.strip() if title else None
            
        # Company name
        if 'brand' in response.url:
            company_name = response.xpath(
                '//div[contains(@class, "company-content")]//text()'
            ).getall()
            item['company_name'] = ' '.join([t.strip() for t in company_name if t.strip()])
        else:
            # Company name - Extract from JavaScript object first
            company = self._extract_from_js_object(response, 'recruiter_company')
            if not company:
                # Fallback: HTML extraction
                company = response.css('div.box-job-info a.text-dark-blue ::text').getall()
                if not company:
                    # Final fallback: thử selector cũ
                    company = response.css('a[class="name"][href*="cong-ty"] ::text').getall()
                company = ' '.join([t.strip() for t in company if t.strip()])
            item['company_name'] = company.strip() if company else None

        # Salary
        if 'brand' in response.url:
            salary = self._extract_important_info(response, 'Mức lương')
        else:
            # Salary - Extract from JavaScript object first
            salary = self._extract_from_js_object(response, 'salary_range')
            if not salary:
                # Fallback: HTML extraction
                salary = response.css('h4.box-header-job__salary::text').get()
            item['salary'] = salary.strip() if salary else None
        
        if 'brand' in response.url:
            # Location (brand pages can use label/value blocks)
            location = self._extract_important_info(response, 'Địa điểm')
            if not location:
                location_texts = response.xpath(
                    '//*[contains(@class, "premium-job-basic-information__content")]'
                    '//*[contains(@class, "item")][.//*[contains(@class, "label") and '
                    '(contains(normalize-space(), "Địa điểm") or contains(normalize-space(), "Địa điểm làm việc"))]]'
                    '//*[contains(@class, "value") or contains(@class, "content")]//text()'
                ).getall()
                location = ' '.join(t.strip() for t in location_texts if t and t.strip())
        else:
            # Location - Extract from JavaScript object first
            location = self._extract_from_js_object(response, 'work_location')
            if not location:
                # Fallback: HTML extraction
                location = response.css("span.hight-light.city-name ::text").getall()
                location = ' '.join(t.strip() for t in location if t.strip())
                location = location.replace("Địa điểm:", "").replace("&nbsp", "")
            item['location'] = location.strip() if location else None

        # Job type
        if 'brand' in response.url:
            job_type = self._extract_important_info(response, 'Hình thức làm việc')
        else:
            job_type = self._extract_important_info_no_brand(response, 'Hình thức làm việc')
        item['job_type'] = job_type.strip() if job_type else None

        # Experience level - Extract from JavaScript object
        experience = self._extract_experience_from_js(response)
        if not experience and 'brand' in response.url:
            # Fallback for brand pages: try HTML extraction
            experience = self._extract_important_info(response, 'Kinh nghiệm')
        if not experience:
            # Final fallback
            experience = 'Không tìm thấy thông tin kinh nghiệm'
        item['experience_level'] = experience.strip() if experience else None

        # Education level
        if 'brand' in response.url:
            education = self._extract_important_info(response, 'Học vấn')
        else:
            education = self._extract_important_info_no_brand(response, 'Học vấn')
        item['education_level'] = education.strip() if education else None

        # Job industry - Extract from JavaScript object first
        industry = self._extract_from_js_object(response, 'job_category')
        if not industry:
            # Fallback: HTML extraction
            industry = response.xpath('//a[contains(@href, "cong-ty") and contains(@class, "text-dark-blue")]/following-sibling::*[1]//text()').get()
        item['job_industry'] = industry.strip() if industry else None

        # Job position
        if 'brand' in response.url:
            position = self._extract_important_info(response, 'Cấp bậc')
        else:
            position = self._extract_important_info_no_brand(response, 'Cấp bậc')
        item['job_position'] = position.strip() if position else None

        # Job deadline
        if 'brand' in response.url:
            deadline = self._extract_important_info(response, 'Hạn nộp hồ sơ')
        else:
            deadline = response.xpath("//i[contains(@class, 'fa-clock')]/following-sibling::span//text()").get()
        item['job_deadline'] = deadline.strip() if deadline else None
        # Job description
        description = self._extract_paragraph(response, 'Mô tả công việc')
        item['job_description'] = description.strip() if description else None

        # Requirements
        requirements = self._extract_paragraph(response, 'Yêu cầu ứng viên')
        item['requirements'] = requirements.strip() if requirements else None

        # Benefits
        benefits = self._extract_paragraph(response, 'Quyền lợi')
        item['benefits'] = benefits.strip() if benefits else None

        # Metadata
        item['source_site'] = 'topcv.vn'
        item['job_url'] = response.url
        item['search_keyword'] = response.meta['keyword']
        item['scraped_at'] = datetime.now().isoformat()

        yield item

    def _extract_important_info_no_brand(self, response, label_text):
        text = response.xpath(f'//*[contains(text(), "{label_text}") and contains(@class,"box-item--title")]/following-sibling::*[position()<=2]//text()').getall()
        return ' '.join([t.strip() for t in text if t.strip()])
    
    def _extract_important_info(self, response, label_text):
        text = response.xpath(f'//*[contains(text(), "{label_text}")]/following-sibling::*[1]//text()').get()
        return text.strip() if text else None

    def _extract_paragraph(self, response, label_text):
        text = response.xpath(f'//*[contains(text(), "{label_text}")]/following-sibling::div[position()<=2]//text()').getall()
        return ' '.join([t.strip() for t in text if t.strip()])

    def _extract_from_js_object(self, response, field_name):
        """Extract information from JavaScript object window.qgTracking"""
        try:
            # Find JavaScript object with window.qgTracking
            js_text = response.xpath('//script[contains(text(), "window.qgTracking")]/text()').get()
            if js_text:
                # Extract field value using regex
                import re
                pattern = f'"{field_name}"\\s*:\\s*"([^"]*)"'
                match = re.search(pattern, js_text)
                if match:
                    value = match.group(1)
                    # Decode Unicode escape sequences if any
                    value = value.encode().decode('unicode_escape') if '\\' in value else value
                    value = value.replace("\\", "")
                    return value
        except Exception as e:
            self.logger.warning(f"Error extracting {field_name} from JS: {e}")
        return None

    def _extract_experience_from_js(self, response):
        """Extract experience information from JavaScript object window.qgTracking"""
        return self._extract_from_js_object(response, 'experience')