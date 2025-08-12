import scrapy
import re
from datetime import datetime
from ..utils import encode_input
from ..items import JobItem


class TopcvSpider(scrapy.Spider):
    name = 'topcv'
    allowed_domains = ['topcv.vn']
    
    def __init__(self, keyword=None, *args, **kwargs):
        super(TopcvSpider, self).__init__(*args, **kwargs)
        self.keyword = keyword or 'data analyst'  # default keyword
        
    def start_requests(self):
        """Generate search URLs based on keyword and location"""
        base_url = 'https://www.topcv.vn/'
        
        search_url = f"{base_url}tim-viec-lam-{encode_input(self.keyword)}"
        
        yield scrapy.Request(
            url=search_url,
            callback=self.parse_search_results,
            meta={'keyword': self.keyword}
        )
    
    def parse_search_results(self, response):
        """Parse the search results page"""
        # Find job listing containers - TopCV specific selectors
        job_listings = response.css('[class="job-list-search-result"]')
        
        self.logger.info(f"Found {len(job_listings)} job listings")
        
        for job in job_listings:
            # Extract job URL
            job_url = job.css('a::attr(href)').get()
            
            yield scrapy.Request(
                url=job_url,
                callback=self.parse_job_detail,
                meta={
                    'keyword': response.meta['keyword'],
                }
            )
            # Test 1 job
            break
        
        # Handle pagination
        next_page = response.css('a[rel="next"]::attr(data-href)').get()
        if next_page:
            yield scrapy.Request(
                url=next_page,
                callback=self.parse_search_results,
                meta=response.meta
            )
        else:
            print("No next page")
    
    def parse_job_detail(self, response):
        """Parse individual job detail page"""
        item = JobItem()
        
        # Basic job information - TopCV specific selectors
        item['job_title'] = self.extract_title(response, '[class*="job-detail__info--title"]') # OK
        item['company_name'] = self.extract_text(response, '[class*="company-name-label"]') # OK
        item['salary'] = self.extract_salary_location_experience(response, "Mức lương") # OK
        item['location'] = self.extract_salary_location_experience(response, "Địa điểm") # OK
        
        # Job details
        item['job_type'] = self.extract_type_edu(response, 'Hình thức làm việc') # OK
        item['experience_level'] = self.extract_salary_location_experience(response, "Kinh nghiệm") # OK
        item['education_level'] = self.extract_type_edu(response, "Học vấn") # OK
        item['job_industry'] = self.extract_text(response, '[class*="job-detail__company--information-item company-field"]') # OK
        
        # Job description and requirements
        item['job_description'] = self.extract_des_require_benefit(response, 'Mô tả công việc') 
        item['requirements'] = self.extract_des_require_benefit(response, 'Yêu cầu ứng viên') 
        item['benefits'] = self.extract_des_require_benefit(response, 'Quyền lợi') 
        
        # Job deadline
        item['job_deadline'] = self.extract_text(response, '[class*="job-detail__info--deadline"]') # OK
        
        # Metadata
        item['source_site'] = 'topcv.vn'
        item['job_url'] = response.url
        item['search_keyword'] = response.meta['keyword']
        item['scraped_at'] = datetime.now().isoformat()
        
        yield item
    
    def extract_title(self, response, selector):
        """Extract title from CSS selector with fallbacks"""
        title = response.css(f'{selector}::text').getall()
        return ' '.join(title).strip() if title else ''
    
    def extract_text(self, response, selector):
        """Extract text from CSS selector with fallbacks"""
        text = response.css(f'{selector}::text').get()
        if not text:
            text = response.css(f'{selector}').get()
        return text.strip() if text else ''

    def extract_salary_location_experience(self, response, label_text):
        try:
            content = response.xpath(f'//*[contains(normalize-space(), "{label_text}")]/following-sibling::div[1]//text()').get()
            return content.strip() if content else ''
        except:
            raise Exception(f"No content found for label: {label_text}")
    
    def extract_type_edu(self, response, label_text):
        try:
            content = response.xpath(f'//*[contains(normalize-space(), "{label_text}")]/following-sibling::div[1]//text()').get()
            return content.strip() if content else ''
        except:
            raise Exception(f"No content found for label: {label_text}")
    
    def extract_des_require_benefit(self, response, label_text):
        try:
            content = response.xpath(f'//h3[contains(normalize-space(), "{label_text}")]/following-sibling::div[1]//text()').getall()
            return ' '.join(content).strip() if content else ''
        except:
            raise Exception(f"No content found for label: {label_text}")