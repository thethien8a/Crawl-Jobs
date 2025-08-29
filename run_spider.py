#!/usr/bin/env python3
"""
Script to run job scraping spiders with custom parameters
Usage: python run_spider.py --spider joboko --keyword "python developer"
"""

import argparse
import sys
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from CrawlJob.spiders.jobsgo_spider import JobsgoSpider
from CrawlJob.spiders.joboko_spider import JobokoSpider
from CrawlJob.spiders.job123_spider import Job123Spider
from CrawlJob.spiders.careerviet_spider import CareervietSpider
from CrawlJob.spiders.jobstreet_spider import JobStreetSpider
from CrawlJob.spiders.linkedin_spider import LinkedinSpider
from CrawlJob.spiders.topcv_spider import TopcvSpider
from CrawlJob.spiders.itviec_spider import ItviecSpider
from CrawlJob.spiders.careerlink_spider import CareerlinkSpider
from CrawlJob.spiders.vietnamworks_spider import VietnamworksSpider


def main():
	# Common practices advice of Scrapy
	parser = argparse.ArgumentParser(description='Run job scraping spiders')
	parser.add_argument('--spider', choices=['jobsgo', 'joboko', '123job', 'careerviet', 'jobstreet', 'linkedin', 'topcv', 'itviec', 'careerlink', 'vietnamworks', 'all'],
					   default='jobsgo', help='Spider to run')
	parser.add_argument('--keyword', default='python developer', 
					   help='Job keyword to search for')
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
			'overwrite': True
		}
	})
	
	# Create crawler process
	process = CrawlerProcess(settings)
	
	try:
		if args.spider == 'jobsgo':
			process.crawl(JobsgoSpider, keyword=args.keyword)
		elif args.spider == 'joboko':
			process.crawl(JobokoSpider, keyword=args.keyword)
		elif args.spider == '123job':
			process.crawl(Job123Spider, keyword=args.keyword)
		elif args.spider == 'careerviet':
			process.crawl(CareervietSpider, keyword=args.keyword)
		elif args.spider == 'jobstreet':
			process.crawl(JobStreetSpider, keyword=args.keyword)
		elif args.spider == 'linkedin':
			process.crawl(LinkedinSpider, keyword=args.keyword)
		elif args.spider == 'topcv':
			process.crawl(TopcvSpider, keyword=args.keyword)
		elif args.spider == 'itviec':
			process.crawl(ItviecSpider, keyword=args.keyword)
		elif args.spider == 'careerlink':
			process.crawl(CareerlinkSpider, keyword=args.keyword)
		elif args.spider == 'vietnamworks':
			process.crawl(VietnamworksSpider, keyword=args.keyword)
		elif args.spider == 'all':
			process.crawl(JobsgoSpider, keyword=args.keyword)
			process.crawl(JobokoSpider, keyword=args.keyword)
			process.crawl(Job123Spider, keyword=args.keyword)
			process.crawl(CareervietSpider, keyword=args.keyword)
			process.crawl(JobStreetSpider, keyword=args.keyword)
			process.crawl(LinkedinSpider, keyword=args.keyword)
			process.crawl(TopcvSpider, keyword=args.keyword)
			# process.crawl(ItviecSpider, keyword=args.keyword)
			process.crawl(CareerlinkSpider, keyword=args.keyword)
			process.crawl(VietnamworksSpider, keyword=args.keyword)
		
		print(f"Starting spider: {args.spider}")
		print(f"Searching for: {args.keyword}")
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
