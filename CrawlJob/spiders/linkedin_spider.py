import time
import random
import os
from datetime import datetime
from urllib.parse import urlencode
import scrapy
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
from ..items import JobItem

# Suppress verbose Selenium and urllib3 logs
import logging
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('selenium.webdriver.remote.remote_connection').setLevel(logging.WARNING)

# Prevent undetected-chromedriver destructor errors
uc.Chrome.__del__ = lambda self: None

load_dotenv()

class LinkedinSpider(scrapy.Spider):
    name = 'linkedin'
    allowed_domains = ['linkedin.com']

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
    }

    def __init__(self, keyword=None,  *args, **kwargs):
        super(LinkedinSpider, self).__init__(*args, **kwargs)
        self.keyword = keyword or 'Data Analyst'
        self.location = 'Vietnam'
        self._max_pages = 1
        self._pages_crawled = 0
        self._click_delay_range = (2, 5)
        self.driver = None
        self._processed_hrefs = set()
        self.__username = os.getenv('LINKEDIN_EMAIL')
        self.__password = os.getenv('LINKEDIN_PASS')


    def _init_driver(self):
        """Initializes the undetected-chromedriver"""
        options = uc.ChromeOptions()
        # Setting headless=True is the correct way for undetected-chromedriver
        # options.add_argument('--headless') 
        options.add_argument(f'--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        
        try:
            self.driver = uc.Chrome(options=options, version_main=None)
            self.logger.info("undetected-chromedriver initialized successfully.")
        except Exception as e:
            self.logger.error(f"Failed to initialize undetected-chromedriver: {e}")
            self.driver = None
        return self.driver

    def _human_like_typing(self, element, text: str):
        """Types a string character by character with random delays."""
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))

    def _login(self):
        """Logs into LinkedIn using credentials from .env file."""
        if not self.driver:
            return False
        
        self.driver.get('https://www.linkedin.com/login')
        wait = WebDriverWait(self.driver, 20)
        
        try:
            # Wait for login form to be ready
            user_input = wait.until(EC.element_to_be_clickable((By.ID, 'username')))
            time.sleep(random.uniform(0.5, 1.0))

            # Fill in credentials with human-like typing
            self._human_like_typing(user_input, self.__username)
            
            time.sleep(random.uniform(0.5, 1.0))
            pass_input = self.driver.find_element(By.ID, 'password')
            self._human_like_typing(pass_input, self.__password)
            
            time.sleep(random.uniform(0.8, 1.5))
            # Click the login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for the main feed to appear as a confirmation of successful login
            wait.until(EC.presence_of_element_located((By.ID, 'global-nav-search')))
            self.logger.info("Successfully logged in to LinkedIn.")
            return True

        except TimeoutException:
            self.logger.error("Login to LinkedIn failed. Timed out waiting for elements.")
            self.driver.save_screenshot('linkedin_login_error.png')
            return False
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during login: {e}")
            self.driver.save_screenshot('linkedin_login_error.png')
            return False
            
    def start_requests(self):
        """Initializes driver, logs in, and starts the scraping process."""
        self._init_driver()
        if not self.driver:
            self.logger.error("Driver could not be initialized. Halting spider.")
            return

        if not self.__username or not self.__password:
            self.logger.error("LinkedIn credentials not found in .env file. Halting spider.")
            return

        if self._login():
            params = {
                'keywords': self.keyword,
                'location': self.location,
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
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='jobs-search-results-list']")))
            except TimeoutException:
                self.logger.error(f"Timed out waiting for job results to load on page {self._pages_crawled}.")
                break

            # Process all visible items on the current page
            yield from self._process_current_visible_items()

            # Find and click the 'Next' button to go to the next page
            try:
                next_button = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button[class*='jobs-search-pagination__button--next']")
                ))
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
        
        job_container = self.driver.find_element(By.CSS_SELECTOR, "ul[class*='ZoMBgxcPjwbXwxVDiHJRnBmTIhQPBYxqqgkZo']")
        job_elements = job_container.find_elements(By.CSS_SELECTOR, "li[id*='ember']")
        for job in job_elements:
            try:
               
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job)
                time.sleep(0.3)
                job.click()
                
                try:
                    job_link = job.find_element(By.CSS_SELECTOR, "a[href*='/jobs/view/']")
                    job_url = job_link.get_attribute('href')
                except Exception:
                    continue
                
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='job-view-layout jobs-details']")))
                time.sleep(0.3)

                item = self._extract_job_from_panel()
                if item:
                    item['source_site'] = 'linkedin.com'
                    item['job_url'] = job_url
                    item['search_keyword'] = self.keyword
                    item['scraped_at'] = datetime.now().isoformat()
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
                return (el.text or '').strip()
            except Exception:
                return ''
        

        item = JobItem()
        
        title = _text_or_empty(By.CSS_SELECTOR, "h1[class*='t-24 t-bold inline']")
        item['job_title'] = title
        
        company = _text_or_empty(By.CSS_SELECTOR, "div[class*='job-details-jobs-unified-top-card__company-name']")
        item['company_name'] = company
        
        location = _text_or_empty(By.CSS_SELECTOR, "span[dir='ltr'] span[class='tvm__text tvm__text--low-emphasis']")
        item['location'] = location
        
        # Lấy mô tả công việc an toàn
        description = _text_or_empty(By.CSS_SELECTOR, "div[class='mt4'] p[dir='ltr']")
        item['job_description'] = description
        
        item['requirements'] = ''
        item['benefits'] = ''

        item['job_type'] = '' 
        item['experience_level'] = ''
        item['education_level'] = ''
        
        try:
            # This div contains industry, employee count, etc
            info_div = self.driver.find_element(By.CSS_SELECTOR, "div.t-14.mt5")
            
            # Use JS to get only the first text node, ignoring child spans
            script = "return arguments[0].firstChild.textContent.trim();"
            industry = self.driver.execute_script(script, info_div)
            item['job_industry'] = industry
        except Exception:
            item['job_industry'] = ''
            
        item['job_position'] = ''
        item['job_deadline'] = ''

        if item['job_title'] == '' :
            return None
        
        return item

    def closed(self, reason):
        """
        Ensures the driver is always quit when the spider is closed,
        preventing orphan processes.
        """
        if hasattr(self, 'driver') and self.driver:
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

    