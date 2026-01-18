
import logging
import random
import re
import time
from datetime import datetime, timedelta

import scrapy
import undetected_chromedriver as uc
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..utils import get_chrome_version, get_chrome_binary_path
from ..items import JobItem
from ..utils import get_chrome_version

# Suppress verbose Selenium and urllib3 logs
logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium.webdriver.remote.remote_connection").setLevel(
    logging.WARNING
)
logger = logging.getLogger(__name__)


class VietnamworksSpider(scrapy.Spider):
    name = "vietnamworks"
    allowed_domains = ["vietnamworks.com"]
    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
    }

    def __init__(self, keyword=None):
        self.keyword = keyword or "data analyst"
        self._max_page = 3
        self._processed_urls = set()
        self._driver = None
        self._init_selenium_driver()

    def _init_selenium_driver(self):
        """Initialize undetected-chromedriver for URL collection"""
        options = uc.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36")
        
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
                "headless": True,
                "use_subprocess": True,
            }
            if chrome_version:
                self.logger.info(f"Using Chrome version: {chrome_version}")
                uc_kwargs["version_main"] = chrome_version
            else:
                self.logger.info("Chrome version not detected, using auto-detection")
                uc_kwargs["version_main"] = None

            if chrome_bin:
                uc_kwargs["browser_executable_path"] = chrome_bin

            self._driver = uc.Chrome(**uc_kwargs)

            logger.info("undetected-chromedriver initialized successfully for VietnamWorks")
        except Exception as e:
            logger.error(f"Failed to initialize undetected-chromedriver: {e}")
            raise

    def start_requests(self):
        """Use Selenium to collect all job URLs, then yield Scrapy requests for parsing"""
        while True:
            try:
                base_url = "https://www.vietnamworks.com/viec-lam"
                search_url = f"{base_url}?q={self.keyword.replace(' ', '-')}"
                self._driver.get(search_url)

                # Wait for initial page load
                WebDriverWait(self._driver, 15).until(
                    lambda d: d.execute_script("return document.readyState")
                    == "complete"
                )

                # Wait for job listings to appear
                try:
                    WebDriverWait(self._driver, 10).until(
                        EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'a[href*="-jv?"]')
                        )
                    )
                except TimeoutException:
                    logger.warning(
                        "No job listings found with primary selector, trying alternatives"
                    )

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
                                meta={"keyword": self.keyword},
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
        """Parse job detail page and yield JobItem to Scrapy pipeline
        
        Includes retry logic to handle StaleElementReferenceException
        """
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                if not self._driver:
                    logger.error("Driver not initialized")
                    return
                    
                # Render detail page with Selenium
                self._driver.get(response.url)

                # Wait for page ready
                WebDriverWait(self._driver, 10).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                
                # Đợi thêm cho dynamic content load
                time.sleep(1)

                # Try to expand hidden content using safe_click
                if self._safe_click("button[aria-label='Xem thêm']", timeout=3):
                    time.sleep(0.7)  # allow content to render

                # Rebuild response with rendered HTML
                rendered_response = response.replace(body=self._driver.page_source)

                # Extract job data using rendered content
                item = self._extract_job_data_from_response(rendered_response)
                if item:
                    yield item
                return  # Thành công, thoát khỏi function

            except StaleElementReferenceException as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Stale element on attempt {attempt + 1} for {response.url}, retrying..."
                    )
                    time.sleep(1)
                else:
                    logger.error(
                        f"Failed after {max_retries} attempts for {response.url}: {e}"
                    )
                    
            except Exception as e:
                logger.error(f"Error in parse_job_detail for {response.url}: {e}")
                return

    def _extract_job_data_from_response(self, response):
        """Extract job data using Scrapy selectors (faster than Selenium)"""
        item = JobItem()
        
        try:
            # Job Title
            item["job_title"] = response.css("h1[name='title']::text").get()

            # Company Name
            item["company_name"] = response.css("a[href*='nha-tuyen-dung']::text").get()

            # Salary
            item["salary"] = response.css("span[class*='cVbwLK']::text").get()

            # Location
            item["location"] = response.css("div[class*='ebdjLi'] span::text").get()

            # Job Type
            item["job_type"] = self._get_general_information(response, "LOẠI HÌNH LÀM VIỆC")

            # Experience Level
            experience_raw = self._get_general_information(response, "SỐ NĂM KINH NGHIỆM TỐI THIỂU")
            item["experience_level"] = f"{experience_raw} năm" if experience_raw else None

            # Education Level
            item["education_level"] = self._get_general_information(response, "TRÌNH ĐỘ HỌC VẤN TỐI THIỂU")

            # Job Description
            item["job_description"] = self._get_descrip_require_benefits(response, "Mô tả công việc")

            # Job Industry
            item["job_industry"] = self._get_general_information(response, "LĨNH VỰC")

            # Job Position
            item["job_position"] = self._get_general_information(response, "CẤP BẬC")

            # Job Deadline
            job_deadline_text = response.xpath("//span[contains(text(), 'Hết hạn trong')]//text()").get()
            if job_deadline_text:
                match = re.search(r"\d+", job_deadline_text)
                number_in_text = int(match.group()) if match else 0
                if "ngày" in job_deadline_text:
                    item["job_deadline"] = (
                        datetime.now() + timedelta(days=number_in_text)
                    ).strftime("%Y-%m-%d")
                else:
                    item["job_deadline"] = (
                        datetime.now() + timedelta(days=number_in_text * 30)
                    ).strftime("%Y-%m-%d")

            # Requirements
            item["requirements"] = self._get_descrip_require_benefits(response, "Yêu cầu")

            # Benefits
            # benefits_section = response.xpath("//h2[contains(@class, 'sc-ab270149-0') and contains(@class, 'iJCYCD') and contains(text(), 'phúc lợi')]/following-sibling::*//text()").getall()
            # item["benefits"] = " ".join([t.strip() for t in benefits_section if t.strip()]) if benefits_section else None
            item["benefits"] = self._get_descrip_require_benefits(response, "phúc lợi dành cho bạn")
            # Metadata
            item["source_site"] = "vietnamworks.com"
            item["job_url"] = response.url
            item["search_keyword"] = self.keyword
            item["scraped_at"] = datetime.now().isoformat()

            # Clean up all fields
            for key in item.fields:
                if key in item and isinstance(item[key], str):
                    item[key] = item[key].strip()

            return item

        except Exception as e:
            logger.error(f"Error extracting job data with Scrapy for {response.url}: {e}")
            return None

    def _get_descrip_require_benefits(self, response, label_text):
        """Find element by text and get the text of the following element"""
        try:
            # Similar logic to _get_text_by_xpath_text but for Scrapy response
            xpath = f"//h2[contains(text(), '{label_text}')]/following-sibling::div//text()"
            texts = response.xpath(xpath).getall()
            if texts:
                return " ".join([t.strip() for t in texts if t.strip()]).strip()
        except Exception:
            pass
        return None

    def _get_general_information(self, response, label_text):
        """Find element by text and get the text of the following element"""
        try:
            # Similar logic to _get_text_by_xpath_text but for Scrapy response
            xpath = f"//label[contains(text(), '{label_text}')]/following-sibling::p//text()"
            texts = response.xpath(xpath).getall()
            if texts:
                return " ".join([t.strip() for t in texts if t.strip()]).strip()
        except Exception:
            pass
        return None

    def _safe_click(self, selector, by=By.CSS_SELECTOR, timeout=3):
        """Click element một cách an toàn, tự động re-fetch nếu stale
        
        Args:
            selector: CSS selector hoặc XPath của element
            by: Loại selector (By.CSS_SELECTOR hoặc By.XPATH)
            timeout: Thời gian chờ tối đa
            
        Returns:
            bool: True nếu click thành công, False nếu thất bại
        """
        if not self._driver:
            return False
            
        try:
            # Đợi element có thể click được
            element = WebDriverWait(self._driver, timeout).until(
                EC.element_to_be_clickable((by, selector))
            )
            
            # Scroll element vào view trước khi click
            self._driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", element
            )
            time.sleep(0.3)
            
            # Re-fetch element sau khi scroll (tránh stale)
            element = self._driver.find_element(by, selector)
            element.click()
            return True
            
        except (TimeoutException, StaleElementReferenceException, NoSuchElementException) as e:
            logger.debug(f"Safe click failed for {selector}: {e}")
            return False

    def _scroll_to_load_content(self, scroll_incre=1000):
        """Scroll down to load dynamic content gradually like a human"""
        try:
            # Get initial page height
            last_height = self._driver.execute_script(
                "return document.body.scrollHeight"
            )

            # Scroll down gradually
            current_position = 0
            while current_position < last_height:
                # Scroll down by increment
                current_position += scroll_incre
                self._driver.execute_script(f"window.scrollTo(0, {current_position});")

                # Random delay between 0.5-1.5 seconds to mimic human behavior
                time.sleep(random.uniform(0.5, 1.5))

                # Check if new content loaded
                new_height = self._driver.execute_script(
                    "return document.body.scrollHeight"
                )
                if new_height > last_height:
                    last_height = new_height

                # If we've reached the bottom, wait a bit for any lazy loading
                if current_position >= last_height:
                    time.sleep(2)
                    # Check one more time for new content
                    final_height = self._driver.execute_script(
                        "return document.body.scrollHeight"
                    )
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
                href = link.get_attribute("href")
                if href:
                    job_urls.add(href)

        except Exception as e:
            logger.error(f"Error extracting job URLs from page: {e}")

        return list(job_urls)

    def _go_to_next_page(self):
        """Navigate to next page, return True if successful"""
        try:
            xpath_next = "//ul[contains(@class, 'pagination')]//li[contains(@class, 'btn-default')]//button[text()='>']"

            # Đợi nút xuất hiện và có thể click được
            next_button = WebDriverWait(self._driver, 7).until(
                EC.element_to_be_clickable((By.XPATH, xpath_next))
            )

            # Scroll xuống để đảm bảo nút nằm trong khung nhìn (tránh bị banner che)
            self._driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                next_button,
            )
            time.sleep(1)  # Chờ một chút sau khi scroll

            next_button.click()
            logger.info("Successfully navigated to the next page.")
            time.sleep(3)  # Chờ trang mới load
            return True

        except (NoSuchElementException, TimeoutException):
            logger.info(
                "Next button not found or not clickable - might be on the last page."
            )
            return False
        except Exception as e:
            logger.warning(f"Error navigating to next page: {e}")
            return False

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