#!/usr/bin/env python3
"""
Script to run job scraping spiders with custom parameters
Usage: python run_spider.py --spider jobsgo --keyword "python developer" --location "Hồ Chí Minh"
"""

import argparse
import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from CrawlJob.spiders.jobsgo_spider import JobsgoSpider
from CrawlJob.spiders.topcv_spider import TopcvSpider


def main():
    parser = argparse.ArgumentParser(description='Run job scraping spiders')
    parser.add_argument('--spider', choices=['jobsgo', 'topcv', 'both'], 
                       default='jobsgo', help='Spider to run')
    parser.add_argument('--keyword', default='python developer', 
                       help='Job keyword to search for')
    parser.add_argument('--location', default='Hồ Chí Minh', 
                       help='Location to search in')
    parser.add_argument('--output', default='jobs.json', 
                       help='Output file for JSON results')
    
    args = parser.parse_args()
    
    # Get project settings
    settings = get_project_settings()
    
    # Configure output
    settings.set('FEEDS', {
        args.output: {
            'format': 'json',
            'encoding': 'utf8',
            'indent': 2,
        }
    })
    
    # Create crawler process
    process = CrawlerProcess(settings)
    
    try:
        if args.spider == 'jobsgo':
            process.crawl(JobsgoSpider, keyword=args.keyword, location=args.location)
        elif args.spider == 'topcv':
            process.crawl(TopcvSpider, keyword=args.keyword, location=args.location)
        elif args.spider == 'both':
            process.crawl(JobsgoSpider, keyword=args.keyword, location=args.location)
            process.crawl(TopcvSpider, keyword=args.keyword, location=args.location)
        
        print(f"Starting spider: {args.spider}")
        print(f"Searching for: {args.keyword}")
        print(f"Location: {args.location}")
        print(f"Output: {args.output}")
        print("-" * 50)
        
        process.start()
        
    except KeyboardInterrupt:
        print("\nSpider interrupted by user")
    except Exception as e:
        print(f"Error running spider: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
