# Suppress verbose Selenium and urllib3 logs
import logging
import os
import random
import re
import time
from datetime import datetime
from urllib.parse import urlencode

import scrapy
import undetected_chromedriver as uc
from dotenv import load_dotenv
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..items import JobItem
from ..utils import get_chrome_version, get_chrome_binary_path

logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium.webdriver.remote.remote_connection").setLevel(
    logging.WARNING
)
# Suppress undetected-chromedriver DEBUG logs
logging.getLogger("undetected_chromedriver").setLevel(logging.WARNING)

# Prevent undetected-chromedriver destructor errors
uc.Chrome.__del__ = lambda self: None

load_dotenv()


class LinkedinSpider(scrapy.Spider):
    name = "linkedin"
    allowed_domains = ["linkedin.com"]

    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
    }

    def __init__(self, keyword=None, *args, **kwargs):
        super(LinkedinSpider, self).__init__(*args, **kwargs)
        self.keyword = keyword or "Data Analyst"
        self.location = "Vietnam"
        self._max_pages = 3
        self._pages_crawled = 0
        self._click_delay_range = (2, 5)
        self.driver = None
        self._processed_hrefs = set()
        self.__username = os.getenv("LINKEDIN_EMAIL")
        self.__password = os.getenv("LINKEDIN_PASS")

    def _init_driver(self):
        """Initializes the undetected-chromedriver with anti-detection for Docker"""
        os.environ["DBUS_SESSION_BUS_ADDRESS"] = "/dev/null"
        
        options = uc.ChromeOptions()
        
        # Essential for Docker
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-setuid-sandbox")
        
        # Anti-detection flags
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins-discovery")
        options.add_argument("--disable-popup-blocking")
        
        # Fake real browser environment
        viewports = [(1366, 768), (1920, 1080), (1440, 900), (1536, 864)]
        width, height = random.choice(viewports)
        options.add_argument(f"--window-size={width},{height}")
        options.add_argument("--start-maximized")
        options.add_argument("--lang=vi,en;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6")
        options.add_argument("--disable-gpu")
        
        # Realistic user-agent (latest Chrome versions - Jan 2026)
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        ]
        options.add_argument(f"--user-agent={random.choice(user_agents)}")

        try:
            chrome_bin = get_chrome_binary_path()
            if chrome_bin:
                self.logger.info(f"Using Chrome binary: {chrome_bin}")
                options.binary_location = chrome_bin
            else:
                self.logger.warning(
                    "Chrome binary not found in PATH; relying on uc auto-detection."
                )

            chrome_version = get_chrome_version()
            uc_kwargs = {
                "options": options,
                "use_subprocess": True,
                "headless": True,  # Use uc's built-in headless (more stealthy)
            }
            if chrome_version:
                self.logger.info(f"Using Chrome version: {chrome_version}")
                uc_kwargs["version_main"] = chrome_version
            else:
                self.logger.info("Chrome version not detected, using auto-detection")
                uc_kwargs["version_main"] = None

            if chrome_bin:
                uc_kwargs["browser_executable_path"] = chrome_bin

            self.driver = uc.Chrome(**uc_kwargs)
            
            # Inject stealth JavaScript to hide automation traces
            self._inject_stealth_js()
            
            self.logger.info("undetected-chromedriver initialized successfully.")
        except Exception as e:
            self.logger.error(f"Failed to initialize undetected-chromedriver: {e}")
            self.driver = None
        return self.driver

    def _inject_stealth_js(self):
        """Inject JavaScript to hide automation traces from bot detection"""
        if not self.driver:
            return
            
        stealth_js = """
        // Hide webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // Fake plugins array
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        
        // Fake languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en', 'vi']
        });
        
        // Fake chrome runtime
        window.chrome = {
            runtime: {},
            loadTimes: function() {},
            csi: function() {},
            app: {}
        };
        
        // Hide automation-related properties
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // Fake connection type
        Object.defineProperty(navigator, 'connection', {
            get: () => ({
                effectiveType: '4g',
                rtt: 50,
                downlink: 10,
                saveData: false
            })
        });
        
        // Fake hardware concurrency (CPU cores)
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 8
        });
        
        // Fake device memory
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => 8
        });
        """
        
        try:
            self.driver.execute_script(stealth_js)
            self.logger.debug("Stealth JavaScript injected successfully")
        except Exception as e:
            self.logger.warning(f"Failed to inject stealth JS: {e}")

    def _human_like_typing(self, element, text: str):
        """Types a string character by character with random delays."""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))

    def _login(self):
        """Logs into LinkedIn using credentials from .env file."""
        if not self.driver:
            return False

        self.driver.get("https://www.linkedin.com/login")
        time.sleep(3)  # Wait for page to fully load
        wait = WebDriverWait(self.driver, 30)

        try:
            # Wait for login form to be ready
            user_input = wait.until(EC.element_to_be_clickable((By.ID, "username")))
            time.sleep(random.uniform(0.5, 1.0))

            # Fill in credentials with human-like typing
            self._human_like_typing(user_input, self.__username)

            time.sleep(random.uniform(0.5, 1.0))
            pass_input = self.driver.find_element(By.ID, "password")
            self._human_like_typing(pass_input, self.__password)

            time.sleep(random.uniform(0.8, 1.5))
            # Click the login button
            login_button = self.driver.find_element(
                By.XPATH, "//button[@type='submit']"
            )
            login_button.click()
            
            # Wait for login to complete (redirect to feed or challenge)
            time.sleep(random.uniform(3, 5))
            
            # Check for various challenge/verification pages
            current_url = self.driver.current_url.lower()
            if any(x in current_url for x in ['challenge', 'checkpoint', 'security-verification', 'authwall']):
                self.logger.error(f"Login blocked by security challenge: {current_url}")
                self.driver.save_screenshot("linkedin_challenge.png")
                return False
            
            # Verify we're actually logged in (feed page or similar)
            if 'feed' in current_url or 'mynetwork' in current_url or 'jobs' in current_url:
                self.logger.info("Login successful!")
                return True
            
            self.logger.warning(f"Unexpected URL after login: {current_url}")
            return True
        
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during login: {e}")
            self.driver.save_screenshot("linkedin_login_error.png")
            return False

    def start_requests(self):
        """Initializes driver, logs in, and starts the scraping process."""
        self._init_driver()
        if not self.driver:
            self.logger.error("Driver could not be initialized. Halting spider.")
            return

        if not self.__username or not self.__password:
            self.logger.error(
                "LinkedIn credentials not found in .env file. Halting spider."
            )
            return

        if self._login():
            params = {
                "keywords": self.keyword,
                "location": self.location,
            }
            url = f"https://www.linkedin.com/jobs/search?{urlencode(params)}"
            # Use a dummy request to trigger the parse method
            yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)
        else:
            self.logger.error("Halting spider due to login failure.")
            return

    def parse(self, response):
        """Main parsing logic after successful login."""
        self.driver.get(response.url)

        wait = WebDriverWait(self.driver, 15)

        # Loop through pages
        while self._pages_crawled < self._max_pages:
            self._pages_crawled += 1
            self.logger.info(f"--- Processing page {self._pages_crawled} ---")

            # Ensure list is present
            try:
                wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div[class*='jobs-search-results-list']")
                    )
                )
            except TimeoutException:
                self.logger.error(
                    f"Timed out waiting for job results to load on page {self._pages_crawled}."
                )
                break

            # Process all visible items on the current page
            yield from self._process_current_visible_items()

            # Find and click the 'Next' button to go to the next page
            try:
                next_button = wait.until(
                    EC.element_to_be_clickable(
                        (
                            By.CSS_SELECTOR,
                            "button[class*='jobs-search-pagination__button--next']",
                        )
                    )
                )
                next_button.click()
                time.sleep(random.uniform(1.5, 2.5))
            except TimeoutException:
                self.logger.info("No 'Next' button found. Reached the last page.")
                break
            except Exception as e:
                self.logger.error(f"Error clicking 'Next' button: {e}")
                break

    def _process_current_visible_items(self):
        wait = WebDriverWait(self.driver, 15)

        time.sleep(1.5)
        
        try:
            job_container = self.driver.find_element(
                By.XPATH, "//ul[li[starts-with(@id, 'ember')]]"
            )
        except Exception as e:
            self.logger.error(f"Error finding job container: {e}")
            return
        
        job_elements = job_container.find_elements(By.CSS_SELECTOR, "li[id*='ember']")
        for job in job_elements:
            try:

                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});", job
                )
                time.sleep(0.3)
                job.click()

                try:
                    job_link = job.find_element(
                        By.CSS_SELECTOR, "a[href*='/jobs/view/']"
                    )
                    job_url = job_link.get_attribute("href")
                except Exception:
                    continue

                wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div[class='job-view-layout jobs-details']")
                    )
                )
                time.sleep(0.3)

                item = self._extract_job_from_panel()
                if item:
                    item["source_site"] = "linkedin.com"
                    item["job_url"] = job_url
                    item["search_keyword"] = self.keyword
                    item["scraped_at"] = datetime.now().isoformat()
                    self._processed_hrefs.add(job_url)
                    yield item

                time.sleep(random.uniform(*self._click_delay_range))

            except Exception as e:
                self.logger.warning(f"Skip job due to error: {e}")
                continue

    def _extract_job_from_panel(self) -> JobItem:
        def _text_or_empty(by, selector):
            try:
                el = self.driver.find_element(by, selector)
                return el.text.strip() if el.text else None
            except Exception:
                return None

        item = JobItem()

        title = _text_or_empty(By.CSS_SELECTOR, "h1[class*='t-24 t-bold inline']")
        item["job_title"] = title

        company = _text_or_empty(
            By.CSS_SELECTOR,
            "div[class*='job-details-jobs-unified-top-card__company-name']",
        )
        item["company_name"] = company

        location = _text_or_empty(
            By.CSS_SELECTOR,
            "span[dir='ltr'] span[class='tvm__text tvm__text--low-emphasis']",
        )
        item["location"] = location

        # Lấy mô tả công việc an toàn
        description = _text_or_empty(By.CSS_SELECTOR, "div[class='mt4'] p[dir='ltr']")
        item["job_description"] = description
        item["salary"] = None
        item["requirements"] = None
        item["benefits"] = None

        # Trường này có thể truy xuất nhưng thôi tôi lười !
        item["job_type"] = None
        
        item["experience_level"] = None
        item["education_level"] = None

        try:
            # Selector này linh hoạt hơn để lấy div chứa Industry, Size, v.v.
            info_div = self.driver.find_element(By.CSS_SELECTOR, "div.t-14.mt5")
            full_info = info_div.text.strip()
            
            if full_info:
                # 1. Tách theo các ký tự phân cách phổ biến của LinkedIn (dấu chấm, xuống dòng, v.v.)
                # Dùng regex để tách theo bullet (·), newline, hoặc 2 khoảng trắng trở lên
                parts = re.split(r'[·\n\r\t●•|]|\s{2,}', full_info)
                industry = parts[0].strip()
                
                # 2. Xử lý trường hợp không có dấu phân cách rõ ràng (ví dụ bị dính liền con số)
                # "Software Development 5.001-10.000" -> "Software Development"
                # Ta tìm vị trí của chữ số đầu tiên để cắt
                digit_match = re.search(r'\d', industry)
                if digit_match:
                    industry = industry[:digit_match.start()].strip()
                
                item["job_industry"] = industry
            else:
                item["job_industry"] = None
        except Exception:
            item["job_industry"] = None

        item["job_position"] = None
        item["job_deadline"] = None

        if item["job_title"] is None:
            return None

        return item

    def closed(self, reason):
        """
        Ensures the driver is always quit when the spider is closed,
        preventing orphan processes.
        """
        if hasattr(self, "driver") and self.driver:
            self.logger.info("Closing the Selenium driver...")
            try:
                self.driver.quit()
                self.logger.info("Driver quit successfully.")
            except Exception as e:
                self.logger.error(f"Error while quitting driver: {e}")
            finally:
                self.driver = None
        else:
            self.logger.info("No active driver to close.")
