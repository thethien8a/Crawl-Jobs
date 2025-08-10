import scrapy
import re
from datetime import datetime
from ..items import JobItem
from ..utils import encode_input, clean_location

class JobsgoSpider(scrapy.Spider):
    name = 'jobsgo'
    allowed_domains = ['jobsgo.vn']
    
    def __init__(self, keyword=None, *args, **kwargs):
        super(JobsgoSpider, self).__init__(*args, **kwargs)
        self.keyword = keyword or 'python developer'  # default keyword
        
    def start_requests(self):
        """Generate search URLs based on keyword and location"""
        base_url = 'https://jobsgo.vn/'
        
        search_word = encode_input(self.keyword)
        
        search_url = f"{base_url}viec-lam-{search_word}.html"
        
        yield scrapy.Request(
            url=search_url,
            callback=self.parse_search_results,
            meta={'keyword': self.keyword}
        )
    
    def parse_search_results(self, response):
        """Parse the search results page"""
        # Find job listing links
        job_links = response.css('a[href*="/viec-lam/"]::attr(href)').getall()
        
        job_urls = []
        for link in job_links:
            if link and 'viec-lam/' in link and link.endswith('.html') and len(link.split('-')) > 3:
                job_urls.append(link)
        
        # Remove duplicates url link
        seen = set()
        unique_job_urls = []
        for url in job_urls:
            if url not in seen:
                seen.add(url)
                unique_job_urls.append(url)
        
        self.logger.info(f"Found {len(unique_job_urls)} job listings")
        
        for job_url in unique_job_urls:
            yield scrapy.Request(
                url=job_url,
                callback=self.parse_job_detail,
                meta={
                    'keyword': response.meta['keyword'],
                }
            )
        
        # Handle pagination
        next_page = response.css('li[class="next"] a::attr(href)').get()
        if next_page:
            yield scrapy.Request(
                url=next_page,
                callback=self.parse_search_results,
                meta=response.meta
            )
        else:
            self.logger.info("No more pages to crawl")
    
    def parse_job_detail(self, response):
        """Parse individual job detail page"""
        item = JobItem()

        # Title
        title = self.extract_text(response, '[class="job-title mb-2 mb-sm-3 fs-4"]')
        item['job_title'] = title 
        
        # Company name - lấy tên công ty từ link tới trang tuyển dụng công ty 
        company = response.css('[class="fw-semibold pe-3 mb-0 pt-4 mt-2"]::text').get()
        item['company_name'] = (company or '')
        
        # Meta list ngay dưới tiêu đề: Mức lương / Hạn nộp / Địa điểm
        item['salary'] = self.extract_value_by_label(response, 'Mức lương')
        item['job_deadline'] = self.extract_value_by_label(response, 'Hạn nộp')
        item['location'] = clean_location(response.css('a[href="#places"].position-relative.text-truncate.d-inline-block::text').get()) 
        
        # Thông tin chung (panel bên dưới)
        item['job_type'] = self.extract_common_section_value(response, 'Loại hình') 
        item['experience_level'] = self.extract_common_section_value(response, 'Yêu cầu kinh nghiệm')
        item['education_level'] = self.extract_common_section_value(response, 'Yêu cầu bằng cấp')
        item['job_industry'] = self.extract_common_section_links(response, 'Ngành nghề')
        
        # Job description and requirements (lấy từ các section tiêu đề h3)
        item['job_description'] = self.extract_section_list_text(response, 'Mô tả công việc')
        item['requirements'] = self.extract_section_list_text(response, 'Yêu cầu công việc')
        item['benefits'] = self.extract_section_list_text(response, 'Quyền lợi được hưởng')
        
        # Metadata
        item['source_site'] = 'jobsgo.vn'
        item['job_url'] = response.url
        item['search_keyword'] = response.meta['keyword']
        item['scraped_at'] = datetime.now().isoformat()
        
        yield item
    
    def extract_text(self, response, selector):
        """Extract text from CSS selector with fallbacks"""
        text = response.css(f'{selector}::text').get()
        if not text:
            self.logger.warning(f"No text found for selector: {selector}")
        return text.strip() if text else ''
    
    def extract_value_by_label(self, response, label_text):
        """Lấy giá trị trong thẻ <li> có chứa nhãn (ví dụ: Mức lương/Hạn nộp/Địa điểm)"""
        texts = response.xpath(f'//li[.//text()[contains(., "{label_text}")]]//strong//text()').get()
        if texts:
            value = texts.strip()
        else:
            value = ''
        return value
    
    def extract_common_section_value(self, response, label_text):
        """Trong khối 'Thông Tin Chung', lấy strong ngay sau nhãn label_text"""
        texts = response.xpath(f'//*[contains(normalize-space(), "{label_text}")]/following-sibling::strong[1]//text()').getall()
        return ' '.join([t.strip() for t in texts if t and t.strip()])
    
    def extract_common_section_links(self, response, label_text):
        """Trong khối 'Thông Tin Chung', lấy danh sách link text ngay sau nhãn (ví dụ: Ngành nghề)"""
        link_texts = response.xpath(f'//*[contains(normalize-space(), "{label_text}")]/following-sibling::strong[1]//a/text()').getall()
        if link_texts:
            return ', '.join([' '.join(t.split()) for t in link_texts if t and t.strip()])
        # Fallback: lấy mọi text trong strong
        texts = response.xpath(f'//*[contains(normalize-space(), "{label_text}")]/following-sibling::strong[1]//text()').getall()
        return ' '.join([t.strip() for t in texts if t and t.strip()])
    
    def extract_section_list_text(self, response, heading_text):
        """Ghép các <li> nằm trong ul ngay sau tiêu đề h3 có chứa heading_text"""
        parts = response.xpath(f'//h2[contains(normalize-space(.), "{heading_text}")]/following-sibling::ul[1]//li//text() | '
                               f'//h3[contains(normalize-space(.), "{heading_text}")]/following-sibling::ul[1]//li//text()').getall()
        if parts:
            joined = ' '.join([' '.join(p.split()) for p in parts if p and p.strip()])
            return joined
        # Fallback: lấy đoạn văn đầu tiên sau heading
        para = response.xpath(f'//h2[contains(normalize-space(.), "{heading_text}")]/following-sibling::*[1]//text() | '
                              f'//h3[contains(normalize-space(.), "{heading_text}")]/following-sibling::*[1]//text()').getall()
        return ' '.join([' '.join(p.split()) for p in para if p and p.strip()])
