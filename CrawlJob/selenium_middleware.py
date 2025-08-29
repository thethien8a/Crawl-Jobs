"""
Selenium middleware for handling JavaScript-heavy websites like JobOKO
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from scrapy.http import HtmlResponse
from scrapy.exceptions import NotConfigured
import logging

logger = logging.getLogger(__name__)


class SeleniumMiddleware:
    """Selenium middleware to render JavaScript pages"""
    
    def __init__(self, crawler):
        self.crawler = crawler
        
        # Chrome options for stealth mode
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in background
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent to mimic real browser
        chrome_options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Window size
        chrome_options.add_argument('--window-size=1920,1080')
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute script to hide webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            logger.info("Selenium Chrome driver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Selenium driver: {e}")
            raise NotConfigured('Selenium driver failed to initialize')
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)
    
    def process_request(self, request, spider):
        """Process request using Selenium for JavaScript rendering"""

        # Use Selenium for JobOKO and VietnamWorks spiders
        if spider.name not in ['joboko', 'vietnamworks']:
            return None
            
        try:
            logger.info(f"Processing request with Selenium: {request.url}")
            
            # Navigate to the page
            self.driver.get(request.url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            
            # Try wait for either job list or job detail indicators
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="-xvi"]')),
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[class*="job"]')),
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[class*="detail"]')),
                    )
                )
            except Exception as e:
                logger.warning(f"Timeout waiting for elements, continuing anyway: {e}")
            
            # Additional small delay for dynamic content
            time.sleep(2)
            
            # Get page source after JavaScript execution
            body = self.driver.page_source
            
            # Create Scrapy response object
            response = HtmlResponse(
                url=request.url,
                body=body,
                encoding='utf-8',
                request=request
            )
            
            logger.info(f"Successfully rendered page with Selenium: {request.url}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing request with Selenium: {e}")
            return None
    
    def spider_closed(self, spider):
        """Clean up Selenium driver when spider closes"""
        if hasattr(self, 'driver'):
            self.driver.quit()
            logger.info("Selenium driver closed")
