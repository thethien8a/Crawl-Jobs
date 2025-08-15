import scrapy
from datetime import datetime
from urllib.parse import urljoin
from ..items import JobItem
from ..utils import encode_ascii_slug, clean_text_with_tab


class ItViecSpider(scrapy.Spider):
    name = 'itviec'
    allowed_domains = ['itviec.com']

    def __init__(self, keyword=None, *args, **kwargs):
        super(ItViecSpider, self).__init__(*args, **kwargs)
        self.keyword = keyword or 'phan tich du lieu'
        self._pages_crawled = 0
        self._max_pages = 5

    def start_requests(self):
        base_url = 'https://itviec.com/'
        # Mặc định trang job theo kỹ năng/từ khóa dạng slug không dấu
        # Ví dụ: https://itviec.com/it-jobs/phan-tich-du-lieu
        slug = encode_ascii_slug(self.keyword, '-')
        search_url = urljoin(base_url, f'it-jobs/{slug}')
        yield scrapy.Request(
            url=search_url,
            callback=self.parse_search_results,
            meta={'keyword': self.keyword}
        )

    def parse_search_results(self, response):
        # Thu thập link đến chi tiết job
        # ITviec thay đổi UI thường xuyên; dùng selector tương đối an toàn
        job_links = set()
        for href in response.css('a[href*="it-jobs"], a[href*="job"]::attr(href)').getall():
            if href and '/job/' in href:
                job_links.add(href)

        for href in job_links:
            yield response.follow(
                href,
                callback=self.parse_job_detail,
                meta={'keyword': response.meta.get('keyword', self.keyword)}
            )

        # Phân trang nếu có
        self._pages_crawled += 1
        next_page = response.css('a[rel="next"], a[aria-label="Next"]::attr(href)').get()
        if next_page and self._pages_crawled < self._max_pages:
            yield response.follow(
                next_page,
                callback=self.parse_search_results,
                meta=response.meta
            )

    def parse_job_detail(self, response):
        item = JobItem()

        # Tiêu đề
        title = response.css('h1::text, h1 *::text').get()
        item['job_title'] = (title or '').strip()

        # Công ty
        company = response.css('[class*="company" i]::text, a[href*="company"]::text').get()
        item['company_name'] = (company or '').strip()

        # Lương
        salary = response.xpath('//*[contains(translate(., "LƯƠNGluong", "luongluong"), "luong")]/following-sibling::*[1]//text()').get()
        item['salary'] = (salary or '').strip()

        # Địa điểm
        location = response.xpath('//*[contains(translate(., "ĐỊA DIEMdia diem", "dia diemdia diem"), "dia diem")]/following-sibling::*[1]//text()').get()
        item['location'] = (location or '').strip()

        # Các trường khác (nhiều trang không hiển thị rõ ràng)
        item['job_type'] = ''
        item['experience_level'] = ''
        item['education_level'] = ''
        item['job_industry'] = ''
        item['job_position'] = ''

        # Mô tả, yêu cầu, phúc lợi
        description = ' '.join(t.strip() for t in response.css('[class*="description" i] ::text').getall() if t.strip())
        if not description:
            description = ' '.join(t.strip() for t in response.xpath('//h2[contains(., "Job Description")]/following-sibling::*[1]//text()').getall() if t.strip())
        item['job_description'] = description

        requirements = ' '.join(t.strip() for t in response.xpath('//h2[contains(., "Requirements") or contains(., "Yêu cầu")]/following-sibling::*[1]//text()').getall() if t.strip())
        item['requirements'] = requirements

        benefits = ' '.join(t.strip() for t in response.xpath('//h2[contains(., "Benefits") or contains(., "Quyền lợi")]/following-sibling::*[1]//text()').getall() if t.strip())
        item['benefits'] = benefits

        # Deadline (thường không có rõ)
        item['job_deadline'] = ''

        # Metadata
        item['source_site'] = 'itviec.com'
        item['job_url'] = response.url
        item['search_keyword'] = response.meta.get('keyword', self.keyword)
        item['scraped_at'] = datetime.now().isoformat()

        return item


