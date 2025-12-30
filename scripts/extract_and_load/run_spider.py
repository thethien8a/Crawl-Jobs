#!/usr/bin/env python3
"""
Script to run job scraping spiders with custom parameters
Usage: python run_spider.py --spider joboko --keyword "python developer"
"""

import argparse
import sys
from pathlib import Path
import sys

# Đảm bảo rằng thư mục Crawljob được import đúng cách
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
    
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from CrawlJob.spiders.careerlink_spider import CareerlinkSpider
from CrawlJob.spiders.careerviet_spider import CareervietSpider
from CrawlJob.spiders.itviec_spider import ItviecSpider
from CrawlJob.spiders.job123_spider import Job123Spider
from CrawlJob.spiders.joboko_spider import JobokoSpider
from CrawlJob.spiders.jobsgo_spider import JobsgoSpider
from CrawlJob.spiders.linkedin_spider import LinkedinSpider
from CrawlJob.spiders.topcv_spider import TopcvSpider
from CrawlJob.spiders.vietnamworks_spider import VietnamworksSpider

def main():
    # Common practices advice of Scrapy
    parser = argparse.ArgumentParser(description="Run job scraping spiders")
    parser.add_argument(
        "--spider",
        choices=[
            "jobsgo",
            # "joboko",
            "123job",
            "careerviet",
            # "jobstreet", Trang này không còn tồn tại ở Việt Nam nữa rồi
            "linkedin",
            "topcv",
            "itviec",
            "careerlink",
            "vietnamworks",
            "all",
            "githubactions_version",
            "local_version"
        ],
        default="local_version",
        help="Spider to run",
    )
    parser.add_argument(
        "--keyword", default="data", help="Job keyword to search for"
    )
    parser.add_argument(
        "--output", default="jobs.json", help="Output file for JSON results"
    )

    args = parser.parse_args()

    # Get project settings
    settings = get_project_settings()

    # Configure output
    settings.set(
        "FEEDS",
        {
            args.output: {
                "format": "json",
                "encoding": "utf8",
                "indent": 2,
                "overwrite": True,
            }
        },
    )

    # Create crawler process
    process = CrawlerProcess(settings)

    try:
        if args.spider == "jobsgo":
            process.crawl(JobsgoSpider, keyword=args.keyword)
        # elif args.spider == "joboko":
        #     process.crawl(JobokoSpider, keyword=args.keyword)
        elif args.spider == "123job":
            process.crawl(Job123Spider, keyword=args.keyword)
        elif args.spider == "careerviet":
            process.crawl(CareervietSpider, keyword=args.keyword)
        elif args.spider == "linkedin":
            process.crawl(LinkedinSpider, keyword=args.keyword)
        elif args.spider == "topcv":
            process.crawl(TopcvSpider, keyword=args.keyword)
        elif args.spider == "itviec": 
            process.crawl(ItviecSpider, keyword=args.keyword)
        elif args.spider == "careerlink":
            process.crawl(CareerlinkSpider, keyword=args.keyword)
        elif args.spider == "vietnamworks":
            process.crawl(VietnamworksSpider, keyword=args.keyword)
        elif args.spider == "githubactions_version":
            process.crawl(JobsgoSpider, keyword=args.keyword)
            process.crawl(CareerlinkSpider, keyword=args.keyword)
            process.crawl(VietnamworksSpider, keyword=args.keyword)
            # process.crawl(JobokoSpider, keyword=args.keyword)
            process.crawl(Job123Spider, keyword=args.keyword)
            process.crawl(CareervietSpider, keyword=args.keyword)
            process.crawl(ItviecSpider, keyword=args.keyword)
        elif args.spider == "local_version":
            process.crawl(LinkedinSpider, keyword=args.keyword)
            process.crawl(TopcvSpider, keyword=args.keyword) 
        elif args.spider == "all":
            process.crawl(JobsgoSpider, keyword=args.keyword)
            # process.crawl(JobokoSpider, keyword=args.keyword)
            process.crawl(Job123Spider, keyword=args.keyword)
            process.crawl(CareervietSpider, keyword=args.keyword)
            process.crawl(LinkedinSpider, keyword=args.keyword)
            process.crawl(TopcvSpider, keyword=args.keyword)
            process.crawl(ItviecSpider, keyword=args.keyword)
            process.crawl(CareerlinkSpider, keyword=args.keyword)
            process.crawl(VietnamworksSpider, keyword=args.keyword)

        process.start()

    except KeyboardInterrupt:
        print("\nSpider interrupted by user")
    except Exception as e:
        print(f"Error running spider: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
