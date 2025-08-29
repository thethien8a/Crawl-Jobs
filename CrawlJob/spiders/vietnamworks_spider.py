import random
import scrapy
import time
import logging
import re
from datetime import datetime, timedelta    
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from ..items import JobItem
from ..utils import create_stealth_chrome_options

logger = logging.getLogger(__name__)

class VietnamworksSpider(scrapy.Spider):
    name = 'vietnamworks'
    allowed_domains = ['vietnamworks.com']
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
    }    
    def __init__(self, keyword=None):
        self.keyword = keyword or 'data analyst'
        self._max_page = 3
        self._processed_urls = set()
        self._driver = None
        self._init_selenium_driver()

    def _init_selenium_driver(self):
        """Initialize Selenium Chrome driver for URL collection with enhanced stealth options"""
        try:
            # Use centralized chrome options configuration
            chrome_options = create_stealth_chrome_options(
                headless=True,  # Set to True for headless mode
                window_size="1920,1080"
            )

            service = Service(ChromeDriverManager().install())
            self._driver = webdriver.Chrome(service=service, options=chrome_options)

            # Execute script to hide webdriver property
            self._driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            logger.info("Selenium Chrome driver initialized successfully for VietnamWorks")
        except Exception as e:
            logger.error(f"Failed to initialize Selenium driver: {e}")
            raise
        

    def start_requests(self):
        """Use Selenium to collect all job URLs, then yield Scrapy requests for parsing"""
        while True:
            try:
                base_url = 'https://www.vietnamworks.com/viec-lam'
                search_url = f"{base_url}?q={self.keyword.replace(' ', '-')}"
                self._driver.get(search_url)

                # Wait for initial page load
                WebDriverWait(self._driver, 15).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )

                # Wait for job listings to appear
                try:
                    WebDriverWait(self._driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="-jv?"]'))
                    )
                except TimeoutException:
                    logger.warning("No job listings found with primary selector, trying alternatives")

                current_page = 1
                
                while current_page <= self._max_page:
                    # Scroll to load all content on current page
                    self._scroll_to_load_content()

                    # Extract job URLs from current page
                    page_urls = self._extract_job_urls_from_page()
                    
                    logger.info(f"Page {current_page}: Found {len(page_urls)} URLs")
                    
                    for url in page_urls:
                        if url not in self._processed_urls:
                            self._processed_urls.add(url)
                            yield scrapy.Request(
                                url=url,
                                callback=self.parse_job_detail,
                                meta={'keyword': self.keyword}
                            )
                    
                    # Try to go to next page
                    if not self._go_to_next_page():
                        logger.info("No more pages available")
                        break

                    current_page += 1
                    time.sleep(2)  # Brief pause between pages

                # If we reach here, everything executed successfully, break the loop
                break

            except Exception as e:
                logger.error(f"Error collecting job URLs with Selenium: {e}")
                logger.info("Retrying start_requests...")
                time.sleep(5)

    def closed(self, reason):
        """Called when the spider is closed by Scrapy - clean up Selenium driver"""
        try:
            self._cleanup_driver()
        except Exception as e:
            logger.error(f"Error during driver cleanup on close: {e}")

    def parse_job_detail(self, response):
        """Parse job detail page and yield JobItem to Scrapy pipeline"""
        try:
            item = self._parse_job_with_selenium(response.url)
            yield item

        except Exception as e:
            logger.error(f"Error in parse_job_detail for {response.url}: {e}")


    def _scroll_to_load_content(self,scroll_incre=1000):
        """Scroll down to load dynamic content gradually like a human"""
        try:
            # Get initial page height
            last_height = self._driver.execute_script("return document.body.scrollHeight")
            
            # Scroll down gradually
            current_position = 0
            while current_position < last_height:
                # Scroll down by increment
                current_position += scroll_incre
                self._driver.execute_script(f"window.scrollTo(0, {current_position});")
                
                # Random delay between 0.5-1.5 seconds to mimic human behavior
                time.sleep(random.uniform(0.5, 1.5))
                
                # Check if new content loaded
                new_height = self._driver.execute_script("return document.body.scrollHeight")
                if new_height > last_height:
                    last_height = new_height
                    
                # If we've reached the bottom, wait a bit for any lazy loading
                if current_position >= last_height:
                    time.sleep(2)
                    # Check one more time for new content
                    final_height = self._driver.execute_script("return document.body.scrollHeight")
                    if final_height > last_height:
                        last_height = final_height
                    else:
                        break

        except Exception as e:
            logger.warning(f"Error during scrolling: {e}")

    def _extract_job_urls_from_page(self):
        """Extract job URLs from current page using multiple selectors"""
        job_urls = set()

        try:
            selector = self._driver.find_elements(By.CSS_SELECTOR, 'a[href*="-jv?"]')
            for link in selector:
                href = link.get_attribute('href')
                if href:
                    job_urls.add(href)

        except Exception as e:
            logger.error(f"Error extracting job URLs from page: {e}")

        return list(job_urls)

    def _parse_job_with_selenium(self, job_url):
        """Parse individual job page using Selenium only"""
        try:
            logger.info(f"Parsing job: {job_url}")
            self._driver.get(job_url)

            # Wait for page to load
            WebDriverWait(self._driver, 10).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            
            try:
                # Find h2 with text "Thông tin việc làm" first, then find button inside it
                h2_element = self._driver.find_element(By.CSS_SELECTOR, "div[class*='dHvFzj']")
                expand_button = h2_element.find_element(By.CSS_SELECTOR, "button[class*='clickable']")
                # Scroll to element to ensure it's visible
                self._driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", expand_button)
                # Wait for element to be clickable
                WebDriverWait(self._driver, 5).until(EC.element_to_be_clickable(expand_button))
                expand_button.click()
            except (NoSuchElementException, Exception):
                logger.info("No expand button found or already expanded")
                
            try:
                expand_button = self._driver.find_element(By.XPATH, '//button[contains(text(), "Xem đầy đủ mô tả công việc")]')
                # Scroll to element to ensure it's visible
                self._driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", expand_button)
                # Wait for element to be clickable
                WebDriverWait(self._driver, 5).until(EC.element_to_be_clickable(expand_button))
                expand_button.click()
                
            except (NoSuchElementException, Exception):
                logger.info("No expand button found or already expanded")
                


            
            # Extract job data using Selenium only
            job_data = self._extract_job_data_with_selenium(job_url)
            return job_data

        except Exception as e:
            logger.error(f"Error parsing job {job_url}: {e}")
            return None

    def _extract_job_data_with_selenium(self, job_url):
        """Extract job data using Selenium WebDriver"""
        item = JobItem()
        
        try:
            # Job Title
            item['job_title'] = self._safe_get_text("h1[name='title']")

            # Company Name
            item['company_name'] = self._safe_get_text("a[href*='nha-tuyen-dung']")

            # Salary
            item['salary'] = self._safe_get_text("span[class*='cVbwLK']")

            # Location
            div_contain_span_location = self._driver.find_element(By.CSS_SELECTOR, "div[class*='ebdjLi']")
            span_location = div_contain_span_location.find_element(By.CSS_SELECTOR, "span")
            item['location'] = span_location.text

            # Job Type
            item['job_type'] = self._get_text_by_xpath_text("LOẠI HÌNH LÀM VIỆC")

            # Experience Level
            item['experience_level'] = self._get_text_by_xpath_text("SỐ NĂM KINH NGHIỆM TỐI THIỂU") + " năm"

            # Education Level
            item['education_level'] = self._get_text_by_xpath_text("TRÌNH ĐỘ HỌC VẤN TỐI THIỂU")

            # Job Description
            item['job_description'] = self._get_text_by_xpath_text("Mô tả công việc")

            # Job Industry
            item['job_industry'] = self._get_text_by_xpath_text("LĨNH VỰC")

            # Job Position
            item['job_position'] = self._get_text_by_xpath_text("CẤP BẬC")

            # Job Deadline
            job_deadline_text = self._safe_get_text("//span[contains(text(), 'Hết hạn trong')]", By.XPATH)
            if job_deadline_text:
                match = re.search(r'\d+', job_deadline_text)
                number_in_text = int(match.group()) if match else 0
                if 'ngày' in job_deadline_text:
                    item['job_deadline'] = (datetime.now() + timedelta(days=number_in_text)).strftime('%Y-%m-%d')
                else:
                    item['job_deadline'] = (datetime.now() + timedelta(days=number_in_text*30)).strftime('%Y-%m-%d')


            # Requirements
            item['requirements'] = self._get_text_by_xpath_text("Yêu cầu")

            # Không có benefits trên trang web
            item['benefits'] = ''

            # Metadata
            item['source_site'] = 'vietnamworks.com'
            item['job_url'] = job_url
            item['search_keyword'] = self.keyword
            item['scraped_at'] = datetime.now().isoformat()

            time.sleep(2)
            
            return item

        except Exception as e:
            logger.error(f"Error extracting job data with Selenium: {e}")
            return None

    def _go_to_next_page(self):
        """Navigate to next page, return True if successful"""
        try:
            next_button = self._driver.find_element(By.CSS_SELECTOR, 'li.page-item.btn-default')
            if next_button.is_displayed():
                next_button.click()
                time.sleep(3) 
                return True
            else:
                return False

        except Exception as e:
            logger.warning(f"Error navigating to next page: {e}")
            return False

    def _get_text_by_xpath_text(self, label_text):
        """Find element by text and get next sibling text"""
        try:
            # Use XPath to find element containing the label text, then get next sibling
            xpath = f"//*[contains(text(), '{label_text}')]/following-sibling::*[1]"
            element = self._driver.find_element(By.XPATH, xpath)
            return element.text.strip()
        except (NoSuchElementException, Exception):
            return ""

    def _cleanup_driver(self):
        """Clean up Selenium driver"""
        if self._driver:
            try:
                self._driver.quit()
                logger.info("Selenium driver cleaned up successfully")
            except Exception as e:
                logger.error(f"Error cleaning up driver: {e}")
            finally:
                self._driver = None

    def _safe_get_text(self, selector, by=By.CSS_SELECTOR):
        """Safely get text from element with fallback to empty string"""
        try:
            element = self._driver.find_element(by, selector)
            return element.text.strip()
        except (NoSuchElementException, Exception):
            return ''