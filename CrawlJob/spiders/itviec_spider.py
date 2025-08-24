import time
import random
from datetime import datetime
from urllib.parse import urlencode
import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from ..items import JobItem

class ItviecSpider(scrapy.Spider):
    """
    ITviec spider using Selenium - similar to LinkedIn spider approach
    """
    name = 'itviec'
    allowed_domains = ['itviec.com']

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
    }

    def __init__(self, keyword=None, username=None, password=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keyword = keyword or 'data analyst'
        self.username = username
        self.password = password
        self._max_pages = 3
        self._click_delay_range = (2, 5)
        self.driver = None
        self._processed_urls = set()

    def _init_driver(self):
        """Initialize Chrome driver with anti-detection"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--window-size=1366,900')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver

    def start_requests(self):
        """Start with search page URL"""
        params = {
            'keywords': self.keyword,
        }
        url = f"https://itviec.com/it-jobs/{self.keyword}"
        yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        """Parse search results page"""
        if self.driver is None:
            self.driver = self._init_driver()

        self.driver.get(response.url)
        wait = WebDriverWait(self.driver, 15)

        # Wait for job cards to load
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h3 a[href*='/it-jobs/']")))

        # Process job cards and load details
        self._process_job_cards()

        return

    def _process_job_cards(self):
        """Process all visible job cards on current page"""
        wait = WebDriverWait(self.driver, 10)

        # Find all job card links
        job_links = self.driver.find_elements(By.CSS_SELECTOR, "h3 a[href*='/it-jobs/']")

        for job_link in job_links:
            try:
                job_url = job_link.get_attribute('href')
                if job_url and '/it-jobs/' in job_url and job_url not in self._processed_urls:
                    self.logger.info(f"Processing job: {job_url}")

                    # Scroll to job link and click
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job_link)
                    time.sleep(0.5)

                    # Click to load job detail
                    job_link.click()

                    # Wait for job detail to load
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h2")))

                    # Extract job data
                    item = self._extract_job_from_detail()
                    if item:
                        item['source_site'] = 'itviec.com'
                        item['job_url'] = job_url
                        item['search_keyword'] = self.keyword
                        item['scraped_at'] = datetime.now().isoformat()
                        self._processed_urls.add(job_url)
                        yield item

                    # Wait before next job
                    time.sleep(random.uniform(*self._click_delay_range))

            except Exception as e:
                self.logger.warning(f"Error processing job card: {e}")
                continue

    def _extract_job_from_detail(self):
        """Extract job data from detail panel"""
        def _safe_get_text(selector, default=''):
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                return element.text.strip()
            except Exception:
                return default

        try:
            item = JobItem()

            # Job title - from h2 in detail panel
            title = _safe_get_text("h2")
            if not title:
                # Fallback: try h1
                title = _safe_get_text("h1")
            item['job_title'] = title

            # Company name - from company link
            company = _safe_get_text("a[href*='/companies/']")
            item['company_name'] = company

            # Salary - check if available or "Sign in to view"
            salary = _safe_get_text(".salary-text")
            if "Sign in" in salary or not salary:
                item['salary'] = "Cần đăng nhập để xem lương"
            else:
                item['salary'] = salary

            # Location - from address text
            location = _safe_get_text(".job-address")
            if not location:
                location = _safe_get_text("[class*='address']")
            item['location'] = location

            # Job type - from job type badge
            job_type = _safe_get_text(".job-type")
            if not job_type:
                job_type = _safe_get_text("[class*='type']")
            item['job_type'] = job_type

            # Experience level - from seniority info
            experience = _safe_get_text(".experience-text")
            if not experience:
                experience = _safe_get_text("[class*='experience']")
            item['experience_level'] = experience

            # Education level - from education info
            education = _safe_get_text(".education-text")
            if not education:
                education = _safe_get_text("[class*='education']")
            item['education_level'] = education

            # Job description - from job description section
            try:
                desc_element = self.driver.find_element(By.CSS_SELECTOR, "[class*='job-description']")
                item['job_description'] = desc_element.text.strip()
            except Exception:
                item['job_description'] = ''

            # Requirements - from requirements section
            try:
                req_element = self.driver.find_element(By.CSS_SELECTOR, "[class*='requirements']")
                item['requirements'] = req_element.text.strip()
            except Exception:
                item['requirements'] = ''

            # Benefits - from benefits section
            try:
                benefits_element = self.driver.find_element(By.CSS_SELECTOR, "[class*='benefits']")
                item['benefits'] = benefits_element.text.strip()
            except Exception:
                item['benefits'] = ''

            # Other fields
            item['job_industry'] = ''
            item['job_position'] = ''
            item['job_deadline'] = ''

            if item['job_title'] == '':
                return None

            return item

        except Exception as e:
            self.logger.error(f"Error extracting job data: {e}")
            return None

    def closed(self, reason):
        """Clean up driver"""
        try:
            if self.driver:
                self.driver.quit()
        except Exception:
            pass
