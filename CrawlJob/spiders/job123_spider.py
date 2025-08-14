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
        self._max_pages = 2

    def start_requests(self):
        base_url = 'https://123job.vn/'
        # Tạo slug đơn giản từ keyword: ghép bằng dấu '-'; giữ Unicode để 123job xử lý
        slug = '-'.join(self.keyword.split()).lower()
        search_path = f'việc-làm-{slug}'
        # Encode path để an toàn khi có ký tự Unicode
        search_url = urljoin(base_url, quote(search_path, safe='/-'))
        yield scrapy.Request(
            url=search_url,
            callback=self.parse_search_results,
            meta={'keyword': self.keyword}
        )

    def parse_search_results(self, response):
        # Thu thập link chi tiết công việc (pattern /viec-lam/<slug>-<id>)
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

        # Phân trang (nếu có)
        next_page = response.css('a[rel="next"]::attr(href)').get()
        if not next_page:
            next_page = response.css('a[aria-label="Next"]::attr(href)').get()
        if not next_page:
            # Fallback: bất kỳ link có page=
            next_page = response.css('a[href*="page="]::attr(href)').get()
        if next_page and self._pages_crawled < self._max_pages:
            self._pages_crawled += 1
            yield response.follow(
                next_page,
                callback=self.parse_search_results,
                meta=response.meta
            )

    def parse_job_detail(self, response):
        item = JobItem()

        # Tiêu đề
        item['job_title'] = self._first_non_empty([
            self._css_text(response, 'h1'),
            self._meta_property(response, 'og:title'),
        ])

        # Công ty
        item['company_name'] = self._first_non_empty([
            self._css_text(response, 'h2 a'),
            self._label_value(response, 'Công ty'),
        ])

        # Lương / Thu nhập
        item['salary'] = self._first_non_empty([
            self._label_value(response, 'Thu nhập'),
            self._label_value(response, 'Mức lương'),
        ])

        # Địa điểm
        item['location'] = self._first_non_empty([
            self._label_value(response, 'Địa điểm làm việc'),
            self._label_value(response, 'Địa điểm'),
        ])

        # Chi tiết
        item['job_type'] = self._first_non_empty([
            self._label_value(response, 'Loại hình'),
            self._label_value(response, 'Hình thức làm việc'),
        ])
        item['experience_level'] = self._label_value(response, 'Kinh nghiệm')
        item['education_level'] = self._first_non_empty([
            self._label_value(response, 'Trình độ học vấn'),
            self._label_value(response, 'Học vấn'),
        ])
        item['job_industry'] = self._first_non_empty([
            self._label_value(response, 'Ngành nghề'),
            self._label_value(response, 'Lĩnh vực'),
        ])
        item['job_position'] = self._first_non_empty([
            self._label_value(response, 'Chức vụ'),
            self._label_value(response, 'Cấp bậc'),
        ])

        # Nội dung mô tả, yêu cầu, quyền lợi
        item['job_description'] = self._section_text(response, 'Mô tả công việc')
        item['requirements'] = self._section_text(response, 'Yêu cầu')
        item['benefits'] = self._section_text(response, 'Quyền lợi')

        # Hạn nộp
        item['job_deadline'] = self._first_non_empty([
            self._label_value(response, 'Hạn nộp'),
            self._label_value(response, 'Hạn nộp hồ sơ'),
        ])

        # Metadata
        item['source_site'] = '123job.vn'
        item['job_url'] = response.url
        item['search_keyword'] = response.meta.get('keyword', self.keyword)
        item['scraped_at'] = datetime.now().isoformat()

        return item

    # ---------- Helpers ----------
    def _css_text(self, response, selector):
        texts = response.css(f'{selector} ::text').getall() if '::' not in selector else response.css(selector).getall()
        if not texts:
            # Try exact selector text only
            texts = response.css(f'{selector}::text').getall()
        return ' '.join(t.strip() for t in texts if t and t.strip())

    def _meta_property(self, response, prop):
        return response.css(f'meta[property="{prop}"]::attr(content)').get() or ''

    def _label_value(self, response, label_text):
        # 1) span label → next span value
        vals = response.xpath(f'//span[normalize-space()="{label_text}:"]/following-sibling::span[1]//text()').getall()
        if not vals:
            vals = response.xpath(f'//span[normalize-space()="{label_text}"]/following-sibling::span[1]//text()').getall()
        if not vals:
            # 2) any element containing label → first following sibling value
            vals = response.xpath(f'//*[contains(normalize-space(), "{label_text}")]/following-sibling::*[1]//text()').getall()
        if not vals:
            # 3) list item variant
            vals = response.xpath(f'//li[.//text()[contains(normalize-space(), "{label_text}")]]//text()').getall()
        joined = ' '.join(v.strip() for v in vals if v and v.strip())
        # Remove label prefix if present
        if joined and joined.lower().startswith(label_text.lower()):
            return joined[len(label_text):].lstrip(':').strip()
        return joined

    def _section_text(self, response, heading_text):
        for xp in (
            f'//h2[contains(normalize-space(), "{heading_text}")]/following-sibling::*[1]//text()',
            f'//h3[contains(normalize-space(), "{heading_text}")]/following-sibling::*[1]//text()',
        ):
            vals = response.xpath(xp).getall()
            if vals:
                return ' '.join(' '.join(v.split()) for v in vals if v and v.strip())
        return ''

    def _first_non_empty(self, candidates):
        for c in candidates:
            if c and str(c).strip():
                return str(c).strip()
        return ''
        