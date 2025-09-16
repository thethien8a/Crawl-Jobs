import os
import time
import random
from datetime import datetime
from selenium.common.exceptions import TimeoutException
import scrapy
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..items import JobItem
from dotenv import load_dotenv
# Suppress verbose Selenium and urllib3 logs
import logging
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.WARNING)
# Prevent undetected-chromedriver destructor errors
uc.Chrome.__del__ = lambda self: None

load_dotenv()
class ItviecSpider(scrapy.Spider):
    """
    ITviec spider using Selenium - similar to LinkedIn spider approach
    """
    name = 'itviec'
    allowed_domains = ['itviec.com']

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
    }

    def __init__(self, keyword=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keyword = keyword or 'data analyst'
        self._pages_crawled = 1
        self._max_pages = 3
        self._click_delay_range = (2, 5)
        self.driver = None
        self._processed_urls = set()
        self.__username = os.getenv('ITVIEC_EMAIL')
        self.__password = os.getenv('ITVIEC_PASS')
    
    def _init_driver(self):
        """Initialize undetected Chrome driver with Cloudflare bypass"""
        # Configure undetected chromedriver options
        options = uc.ChromeOptions()

        # Basic configuration for stability
        options.add_argument(f'--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')

        # Anti-detection measures (undetected-chromedriver already has most of these built-in)
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-default-apps')
        options.add_argument('--disable-sync')
        options.add_argument('--disable-translate')
        options.add_argument('--hide-scrollbars')
        options.add_argument('--no-first-run')
        options.add_argument('--disable-prompt-on-repost')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')

        # Set window size for consistency
        options.add_argument('--window-size=1920,1080')
        driver = uc.Chrome(headless=True, options=options, version_main=None)

        # Additional stealth scripts (optional, as undetected-chromedriver already provides most stealth)
        stealth_scripts = [
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
            "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})",
            "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})",
            """
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
            );
            """,
        ]

        for script in stealth_scripts:
            driver.execute_script(script)

        return driver

    def _login(self):
        """Fast login to ITviec"""
        if self.driver is None:
            self.driver = self._init_driver()
        
        # Navigate to login page
        self.driver.get("https://itviec.com/sign_in")
        
        # Quick wait for page load
        time.sleep(1)
        
        # Wait for email input to be visible
        wait = WebDriverWait(self.driver, 20) # Increased wait time
        try:
            email_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[id='user_email']")))
        except TimeoutException:
            self.logger.error("Failed to find the email input field. The page might be blocked or changed.")
            self.driver.save_screenshot('itviec_login_error.png')
            with open('itviec_login_error.html', 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            self.logger.info("Saved screenshot and page source to 'itviec_login_error.png/html' for debugging.")
            return

        # Quick email input
        email_input.click()
        email_input.clear()
        email_input.send_keys(self.__username)
        
        # Quick password input
        password_input = self.driver.find_element(By.CSS_SELECTOR, "input[id='user_password']")
        password_input.click()
        password_input.clear()
        password_input.send_keys(self.__password)
        
        # Quick submit
        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit' and .//span[contains(text(),'Sign In with Email')]]")
        submit_button.click()
        
        # Wait for login to complete (minimal wait)
        time.sleep(2)
        
        # Quick login verification
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[id='query']")))
            self.logger.info("Successfully logged in to ITviec")
        except TimeoutException:
            self.logger.warning("Login verification timeout - proceeding anyway")

    def start_requests(self):
        """Start crawling with direct Selenium navigation"""
        self._login()

        # Prevent further execution if login failed
        if not self.driver or 'sign_in' in self.driver.current_url:
            self.logger.error("Login failed or was not completed. Halting spider.")
            return
            
        url = f"https://itviec.com/it-jobs/{self.keyword}"

    
        self.driver.get(url)
        wait = WebDriverWait(self.driver, 15)
        
        # Wait for job cards to load
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1[class*='headline-total-jobs']")))
        
        # Process job cards and yield items
        yield from self._process_job_cards()

        
    def _process_job_cards(self):
        """Process all visible job cards on current page"""
        wait = WebDriverWait(self.driver, 10)

        # Find all job card links
        job_links = self.driver.find_elements(By.CSS_SELECTOR, "h3[data-url*='/it-jobs/']")
        self.logger.info(f"Found {len(job_links)} job cards")
        
        for job_link in job_links:
            try:
                job_url = job_link.get_attribute('data-url')
                if job_url and job_url not in self._processed_urls:
                    self.logger.info(f"Processing job: {job_url}")

                    # Scroll to job link and click
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job_link)
                    time.sleep(0.5)

                    # Click to load job detail
                    job_link.click()

                    # Wait for job detail to load
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='preview-job-wrapper']")))

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
        
        try:
            
            # Check if we should continue to next page
            if self._pages_crawled >= self._max_pages:
                return

            # Try multiple selectors for next page button
            next_selectors = [
                "a[rel='next']",
                f"a[href*='page={self._pages_crawled + 1}']"
            ]

            next_button = None
            for selector in next_selectors:
                try:
                    # Use WebDriverWait for proper element loading
                    next_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    self.logger.info(f"Found next page button with selector: {selector}")
                    break
                except:
                    continue

            if next_button:
                # Scroll to button to ensure it's visible
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                time.sleep(1)

                # Click the button
                try:
                    next_button.click()
                except:
                    # Fallback to JavaScript click
                    self.driver.execute_script("arguments[0].click();", next_button)

                # Wait for page to load
                time.sleep(random.uniform(2, 4))

                self.logger.info(f"Moving to page {self._pages_crawled + 1}")
                self._pages_crawled += 1
                # Recursively process next page
                yield from self._process_job_cards()
            else:
                self.logger.info("No next page button found - reached end of results")

        except Exception as e:
            self.logger.warning(f"Error processing next page: {e}")
            return


    def _extract_job_from_detail(self):
        """Extract job data from detail panel"""

        try:
            # Lấy ra wraper của job_detail
            preview_job_wrapper = self.driver.find_element(By.CSS_SELECTOR, "div[class*='preview-job-wrapper']")
            
            item = JobItem()

            # Job title - from h2 in detail panel
            try:
                title = preview_job_wrapper.find_element(By.CSS_SELECTOR, "h2[class*='text-it-black text-hover-red']").text.strip()
                item['job_title'] = title
            except Exception:
                item['job_title'] = None

            # Company name - from company link
            try:
                company = preview_job_wrapper.find_element(By.CSS_SELECTOR, "a[href*='/companies/'][class*='normal-text']").text.strip()
                item['company_name'] = company or None
            except Exception:
                item['company_name'] = None

            # Salary - check if available or "Sign in to view"
            try:
                salary = preview_job_wrapper.find_element(By.CSS_SELECTOR, "span.ips-2.fw-500").text.strip()
                item['salary'] = salary or None
            except Exception:
                item['salary'] = None
            
            # Location - from address text
            try:
                location = preview_job_wrapper.find_element(By.CSS_SELECTOR, "div.d-inline-block.text-dark-grey").text.strip()
                item['location'] = location or None
            except Exception:
                item['location'] = None

            # ITviec không có job type
            item['job_type'] = None

            # ITviec không có experience level
            item['experience_level'] = None

            # Education level - from education info
            item['education_level'] = None

            # Job description - from job description section
            try:
                desc_element = preview_job_wrapper.find_element(By.CSS_SELECTOR, "section[class='job-description']")
                item['job_description'] = desc_element.text.strip()
            except Exception:
                item['job_description'] = None

            # Requirements - from requirements section
            try:
                req_element = preview_job_wrapper.find_element(By.CSS_SELECTOR, "section[class='job-experiences']")
                item['requirements'] = req_element.text.strip()
            except Exception:
                item['requirements'] = None

            # Benefits - from benefits section
            try:
                benefits_element = preview_job_wrapper.find_element(By.CSS_SELECTOR, "section[class='job-why-love-working']")
                item['benefits'] = benefits_element.text.strip()
            except Exception:
                item['benefits'] = None

            # Other fields
            try:
                industry = preview_job_wrapper.find_element(By.CSS_SELECTOR, "div[class='d-inline-flex text-wrap']").text.strip()
                item['job_industry'] = industry or None
            except Exception:
                item['job_industry'] = None

            # ITviec không có job position
            item['job_position'] = None

            # ITviec không có job deadline
            item['job_deadline'] = None


            return item

        except Exception as e:
            self.logger.error(f"Error extracting job data: {e}")
            return None

    def closed(self, reason):
        """Robust driver cleanup for Windows compatibility"""
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
            self.logger.info("Driver cleanup completed successfully")
        else:
            self.logger.info("No driver to cleanup")

        # Always set driver to None to prevent future access
        self.driver = None
        self.logger.info("Driver reference cleared")
