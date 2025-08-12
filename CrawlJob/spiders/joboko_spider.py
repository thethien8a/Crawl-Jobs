import scrapy
from datetime import datetime
from urllib.parse import urljoin
from ..items import JobItem
from ..utils import encode_joboko_input, clean_location


class JobokoSpider(scrapy.Spider):
    name = 'joboko'
    allowed_domains = ['vn.joboko.com']

    def __init__(self, keyword=None, *args, **kwargs):
        super(JobokoSpider, self).__init__(*args, **kwargs)
        self.keyword = keyword or 'data analyst'

    def start_requests(self):
        base_url = 'https://vn.joboko.com/'
        search_path = f"tim-viec-lam-{encode_joboko_input(self.keyword)}"
        search_url = urljoin(base_url, search_path)
        yield scrapy.Request(
            url=search_url,
            callback=self.parse_search_results,
            meta={'keyword': self.keyword}
        )

    def parse_search_results(self, response):
        # Thu thập link chi tiết công việc: pattern đuôi -xvi<ID>
        job_links = response.css('a[href*="-xvi"]::attr(href)').getall()
        seen = set()
        unique_links = []
        for link in job_links:
            if not link:
                continue
            full_url = urljoin(response.url, link)
            if full_url not in seen:
                seen.add(full_url)
                unique_links.append(full_url)

        self.logger.info(f"Found {len(unique_links)} job links on {response.url}")

        for job_url in unique_links:
            yield scrapy.Request(
                url=job_url,
                callback=self.parse_job_detail,
                meta={'keyword': response.meta.get('keyword', self.keyword)}
            )

        # Phân trang: ưu tiên rel=next, fallback bắt '?p='
        next_page = response.css('a[rel="next"]::attr(href)').get()
        if not next_page:
            candidates = response.css('a[href*="?p="]::attr(href)').getall()
            if candidates:
                # Nếu có nhiều link, ưu tiên link chứa p lớn nhất để tiến tới
                try:
                    def extract_p(u):
                        from urllib.parse import urlparse, parse_qs
                        qs = parse_qs(urlparse(u).query)
                        return int(qs.get('p', ['0'])[0])
                    candidates_sorted = sorted(candidates, key=extract_p)
                    next_page = candidates_sorted[-1]
                except Exception:
                    next_page = candidates[-1]
        if next_page:
            yield scrapy.Request(
                url=urljoin(response.url, next_page),
                callback=self.parse_search_results,
                meta=response.meta
            )

    def parse_job_detail(self, response):
        item = JobItem()

        # Tiêu đề
        title = self._first_non_empty([
            self._css_text(response, 'h1'),
            self._css_text(response, 'h2'),
            self._meta_property(response, 'og:title'),
        ])
        item['job_title'] = title

        # Tên công ty - nhiều trang liên kết về trang công ty có hậu tố -xci<ID>
        company = self._first_non_empty([
            self._css_text(response, 'a[href*="-xci"]'),
            self._label_value(response, 'Công ty'),
        ])
        item['company_name'] = company or ''

        # Meta khu vực/salary/deadline
        item['salary'] = self._first_non_empty([
            self._label_value(response, 'Mức lương'),
            self._label_value(response, 'Lương'),
        ]) or ''

        location_raw = self._first_non_empty([
            self._label_value(response, 'Địa điểm'),
            self._label_value(response, 'Nơi làm việc'),
            self._label_value(response, 'Khu vực'),
        ])
        item['location'] = clean_location(location_raw or '')

        # Details
        item['job_type'] = self._first_non_empty([
            self._label_value(response, 'Hình thức'),
            self._label_value(response, 'Loại hình'),
        ]) or ''
        item['experience_level'] = self._label_value(response, 'Kinh nghiệm') or ''
        item['education_level'] = self._first_non_empty([
            self._label_value(response, 'Trình độ học vấn'),
            self._label_value(response, 'Học vấn'),
        ]) or ''
        item['job_industry'] = self._first_non_empty([
            self._label_value(response, 'Ngành nghề'),
            self._label_value(response, 'Lĩnh vực'),
        ]) or ''

        # Nội dung mô tả/yêu cầu/quyền lợi
        item['job_description'] = self._section_text(response, 'Mô tả công việc')
        item['requirements'] = self._section_text(response, 'Yêu cầu')
        item['benefits'] = self._section_text(response, 'Quyền lợi')

        # Hạn nộp
        item['job_deadline'] = self._first_non_empty([
            self._label_value(response, 'Hạn nộp'),
            self._label_value(response, 'Hạn cuối'),
        ]) or ''

        # Metadata
        item['source_site'] = 'vn.joboko.com'
        item['job_url'] = response.url
        item['search_keyword'] = response.meta.get('keyword', self.keyword)
        item['scraped_at'] = datetime.now().isoformat()

        yield item

    # ---------- Helper methods ----------
    def _css_text(self, response, selector):
        txts = response.css(f'{selector}::text').getall()
        return ' '.join([t.strip() for t in txts if t and t.strip()]) if txts else ''

    def _meta_property(self, response, prop):
        return response.css(f'meta[property="{prop}"]::attr(content)').get() or ''

    def _label_value(self, response, label_text):
        # Tìm node chứa nhãn rồi lấy phần tử kế sau
        xp_variants = [
            f'//*[contains(normalize-space(), "{label_text}")]/following-sibling::*[1]//text()',
            f'//*[contains(normalize-space(), "{label_text}")]/ancestor::*[1]/following-sibling::*[1]//text()',
            f'//li[.//text()[contains(., "{label_text}")]]//*[self::strong or self::span or self::div][1]//text()',
        ]
        for xp in xp_variants:
            vals = response.xpath(xp).getall()
            if vals:
                joined = ' '.join([' '.join(v.split()) for v in vals if v and v.strip()]).strip()
                if joined:
                    return joined
        return ''

    def _section_text(self, response, heading_text):
        xp_variants = [
            f'//h2[contains(normalize-space(), "{heading_text}")]/following-sibling::*[1]//text()',
            f'//h3[contains(normalize-space(), "{heading_text}")]/following-sibling::*[1]//text()',
        ]
        for xp in xp_variants:
            vals = response.xpath(xp).getall()
            if vals:
                return ' '.join([' '.join(v.split()) for v in vals if v and v.strip()])
        return ''

    def _first_non_empty(self, candidates):
        for c in candidates:
            if c and str(c).strip():
                return c.strip()
        return ''
