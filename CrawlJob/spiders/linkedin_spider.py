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


class LinkedinSpider(scrapy.Spider):
    name = 'linkedin'
    allowed_domains = ['linkedin.com']

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
    }

    def __init__(self, keyword=None, location=None, *args, **kwargs):
        super(LinkedinSpider, self).__init__(*args, **kwargs)
        self.keyword = keyword or 'Data Analyst'
        self.location = location or 'Vietnam'
        self._max_batches = 3  # Number of times to click "See more jobs/Xem thêm việc làm"
        self._click_delay_range = (2, 5)
        self.driver = None
        self._processed_hrefs = set() 

    def _init_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                     'AppleWebKit/537.36 (KHTML, like Gecko) '
                                     'Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--window-size=1366,900')
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver

    def start_requests(self):
        params = {
            'keywords': self.keyword,
            'location': self.location,
        }
        url = f"https://www.linkedin.com/jobs/search?{urlencode(params)}"
        yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        if self.driver is None:
            self.driver = self._init_driver()
        self.driver.get(response.url)

        wait = WebDriverWait(self.driver, 15)
        
        # Thử đóng popup yêu cầu đăng nhập nếu xuất hiện
        self._dismiss_login_modal()
        
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='results-context']")))

        batches = 0
        while True:
            # Process any newly visible items
            yield from self._process_current_visible_items()

            if batches >= self._max_batches:
                break

            # Try clicking the "See more jobs" button
            prev_count = self._count_job_links()
            load_more_btn = self._find_load_more_button()
            if not load_more_btn:
                break
            try:
                
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", load_more_btn)
                time.sleep(0.5)
                load_more_btn.click()
                
                # wait for new items to load (count increases)
                self._wait_for_more_items(prev_count, timeout=15)
                batches += 1
                time.sleep(random.uniform(*self._click_delay_range))
            
            except Exception as e:
                self.logger.info(f"Stop loading more due to: {e}")
                break

        return

    def _count_job_links(self) -> int:
        try:
            return len(self.driver.find_elements(By.CSS_SELECTOR, "main a[href*='/jobs/view/']"))
        except Exception:
            return 0

    def _find_load_more_button(self):
        # Vietnamese: "Xem thêm việc làm"; English: "See more jobs"
        xpaths = [
            "//button[contains(., 'Xem thêm việc làm')]",
            "//button[contains(., 'See more jobs')]",
        ]
        for xp in xpaths:
            try:
                btn = self.driver.find_element(By.XPATH, xp)
                if btn and btn.is_enabled():
                    return btn
            except Exception:
                continue
        return None

    def _wait_for_more_items(self, prev_count: int, timeout: int = 15):
        end = time.time() + timeout
        while time.time() < end:
            curr = self._count_job_links()
            if curr > prev_count:
                return
            time.sleep(0.5)
    
    def _process_current_visible_items(self):
        wait = WebDriverWait(self.driver, 15)
        # Lấy đúng các thẻ anchor của danh sách kết quả thay vì container <ul>
        anchors = self.driver.find_elements(
            By.CSS_SELECTOR, "ul.jobs-search__results-list a[href*='/jobs/view/']"
        )
        ordered = []

        # Set để kiểm tra href có tồn tại trong view hiện tại không
        seen_local = set()
        for a in anchors:
            try:
                href = a.get_attribute('href')
                # Điều kiện: có href hợp lệ, chưa thấy trong vòng lặp này và chưa xử lý từ trước
                if href and '/jobs/view/' in href and href not in seen_local and href not in self._processed_hrefs:
                    seen_local.add(href)
                    ordered.append((a, href))
            except Exception:
                continue

        for a, href in ordered:
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", a)
                time.sleep(0.3)
                a.click()
                # Đóng popup (nếu xuất hiện) trước khi chờ panel details
                self._dismiss_login_modal()
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[class*='details-pane']")))
                time.sleep(0.3)

                item = self._extract_job_from_panel()
                if item:
                    item['source_site'] = 'linkedin.com'
                    item['job_url'] = href
                    item['search_keyword'] = self.keyword
                    item['scraped_at'] = datetime.now().isoformat()
                    self._processed_hrefs.add(href)
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
        
        def section_text(keyword: str) -> str:
            try:
                sec = self.driver.find_elements(By.XPATH, f"//h3[contains(normalize-space(.), '{keyword}')]/following-sibling::span[1]")
                if sec:
                    return (sec[0].text or '').strip()
            except Exception:
                return ''
            return ''

        item = JobItem()
        
        title = _text_or_empty(By.CSS_SELECTOR, "h2[class*='top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title']")
        item['job_title'] = title
        
        company = _text_or_empty(By.CSS_SELECTOR, "a[class*='topcard__org-name-link topcard__flavor--black-link']")
        item['company_name'] = company
        
        # Sửa selector: hai class cần nối bằng dấu chấm
        location = _text_or_empty(By.CSS_SELECTOR, "span.topcard__flavor.topcard__flavor--bullet")
        item['location'] = location
        
        # Lấy mô tả công việc an toàn
        try:
            desc_el = self.driver.find_element(By.CSS_SELECTOR, "div[class*='show-more-less-html__markup']")
            item['job_description'] = (desc_el.get_attribute('textContent') or '').strip()
        except Exception:
            item['job_description'] = ''
            
        item['requirements'] = ''
        item['benefits'] = ''

        item['job_type'] = section_text('Employment type') 
        item['experience_level'] = section_text('Seniority level')
        item['education_level'] = ''
        item['job_industry'] = section_text('Industries')
        item['job_position'] = ''
        item['job_deadline'] = ''

        if item['job_title'] == '' :
            return None
        
        return item

    def closed(self, reason):
        try:
            if self.driver:
                self.driver.quit()
        except Exception:
            pass

    def _dismiss_login_modal(self) -> bool:
        """Cố gắng đóng popup đăng nhập của LinkedIn nếu nó xuất hiện.

        Trả về True nếu đã đóng được, False nếu không tìm thấy/không đóng.
        """
        candidates = [
            (By.CSS_SELECTOR, "svg.artdeco-icon.lazy-loaded")
        ]
        for by, sel in candidates:
            try:
                btn = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((by, sel)))
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                time.sleep(0.1)
                try:
                    btn.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", btn)
                time.sleep(0.2)
                return True
            except TimeoutException:
                continue
            except Exception:
                continue

        # Fallback: gửi phím ESC để đóng overlay nếu có
        try:
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        except Exception:
            pass
        return False
