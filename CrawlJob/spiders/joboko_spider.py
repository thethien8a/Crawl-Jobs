import re
from datetime import datetime
from urllib.parse import urljoin

import scrapy

from ..items import JobItem
from ..utils import encode_joboko_input, regex_find_date


class JobokoSpider(scrapy.Spider):
    name = "joboko"
    allowed_domains = ["vn.joboko.com"]

    def __init__(self, keyword=None, *args, **kwargs):
        super(JobokoSpider, self).__init__(*args, **kwargs)
        self.keyword = keyword or "data analyst"
        self._max_page = 3

    def start_requests(self):
        base_url = "https://vn.joboko.com/"
        search_path = f"jobs?q={encode_joboko_input(self.keyword)}"
        search_url = urljoin(base_url, search_path)
        
        for page in range(1, self._max_page + 1):
            yield scrapy.Request(
                url=f"{search_url}&p={page}",
                callback=self.parse_search_results,
                meta={"keyword": self.keyword},
            )

    def parse_search_results(self, response):
        # Thu thập link chi tiết công việc:
        url_jobs = response.css(
            'div.nw-job-list__list a[href*="viec-lam"]::attr(href)'
        ).getall()
        if url_jobs:
            self.logger.info(f"Found {len(url_jobs)} job links on {response.url}")
            for job_url in url_jobs:
                yield response.follow(
                    job_url,
                    callback=self.parse_job_detail,
                    meta={"keyword": response.meta.get("keyword", self.keyword)},
                )

    def parse_job_detail(self, response):
        item = JobItem()

        # Job title
        item["job_title"] = self._css_text(response, "nw-company-hero__title")

        # Job deadline
        item["job_deadline"] = regex_find_date(self._css_text(response, "mt-1 fz-16"))
        # Company name
        item["company_name"] = self._css_text(response, "nw-company-hero__text")
        # Salary
        item["salary"] = self._xpath_text(response, "Thu nhập")
        # Location
        item["location"] = self._xpath_text(response, "Địa điểm làm việc")

        if item["location"] is None:
            item["location"] = response.css(
                "span.fz-13.fw-medium.letter-spacing-1.c-text-2::text"
            ).get()

        item["job_type"] = self._xpath_text(response, "Loại hình")
        item["experience_level"] = self._xpath_text(response, "Kinh nghiệm")

        # Education level & industry không luôn có sẵn
        item["education_level"] = None
        item["job_industry"] = None
        
        # Job position
        item["job_position"] = self._xpath_text(response, "Chức vụ")

        item["job_description"] = self._xpath_paragraph(response, "Mô tả công việc")
        item["requirements"] = self._xpath_paragraph(response, "Yêu cầu")
        item["benefits"] = self._xpath_paragraph(response, "Quyền lợi")

        # Metadata
        item["source_site"] = "vn.joboko.com"
        item["job_url"] = response.url
        item["search_keyword"] = response.meta.get("keyword", self.keyword)
        item["scraped_at"] = datetime.now().isoformat()

        yield item

    def _css_text(self, response, css_selector):
        try:
            parts = response.css(f'[class*="{css_selector}"] ::text').getall()
            return " ".join(p.strip() for p in parts if p.strip())
        except Exception:
            return None

    def _xpath_text(self, response, text_extract):
        try:
            full = response.xpath(
                f'//text()[contains(., "{text_extract}")]/following-sibling::*/text()'
            ).get()
            return full.strip()
        except Exception:
            return None

    def _xpath_paragraph(self, response, text_extract):
        try:
            paragraphs = response.xpath(
                f'//*[contains(normalize-space(), "{text_extract}")]/following-sibling::*[1]//text()'
            ).getall()
            if not paragraphs:
                return None
            return " ".join(p.strip() for p in paragraphs if p.strip())
        except Exception:
            return None
