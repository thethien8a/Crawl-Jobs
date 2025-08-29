import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from CrawlJob.spiders.itviec_spider import ItviecSpider

# Create spider instance
itviec_spider = ItviecSpider(keyword='data analyst')

# Call login method
try:
    itviec_spider._login()
    print("Login successful!")
except Exception as e:
    print(f"Login failed: {e}")
finally:
    itviec_spider.closed(None)