#!/usr/bin/env python3
"""
Test script for ITVIEC spider with undetected chromedriver
Tests Cloudflare bypass functionality
"""

import os
import random
import sys
import time

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from CrawlJob.spiders.itviec_spider import ItviecSpider


def test_itviec_login():
    """Test ITVIEC login with undetected chromedriver"""
    print("🚀 Testing ITVIEC Login with Undetected ChromeDriver")
    print("=" * 60)

    # Check environment variables
    username = os.getenv("ITVIEC_EMAIL")
    password = os.getenv("ITVIEC_PASS")

    if not username or not password:
        print("❌ Missing credentials!")
        print("📝 Please set ITVIEC_EMAIL and ITVIEC_PASS in your .env file")
        print("Example:")
        print("ITVIEC_EMAIL=your_email@example.com")
        print("ITVIEC_PASS=your_password")
        return False

    print(f"✅ Credentials found for: {username}")

    # Create spider instance
    spider = ItviecSpider(keyword="data analyst")

    try:
        print("🌐 Initializing undetected Chrome driver...")
        driver = spider._init_driver()
        print("✅ Driver initialized successfully")

        print("🔐 Attempting login...")
        spider._login()
        print("✅ Login completed")

        # Verify login success
        try:
            # Check for dashboard or profile elements
            driver.get("https://itviec.com/dashboard")
            time.sleep(3)

            # Check if we're logged in
            if "dashboard" in driver.current_url or "profile" in driver.current_url:
                print("🎉 Login successful! Dashboard accessible.")
                return True
            else:
                print("⚠️  Login may have failed - not redirected to dashboard")
                return False

        except Exception as e:
            print(f"⚠️  Could not verify login status: {e}")
            return False

    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False

    finally:
        # Cleanup
        try:
            if hasattr(spider, "driver") and spider.driver:
                spider.driver.quit()
                print("🧹 Driver cleanup completed")
        except:
            pass


def test_cloudflare_detection():
    """Test if Cloudflare challenge is triggered"""
    print("\n🔍 Testing Cloudflare Challenge Detection")
    print("=" * 60)

    spider = ItviecSpider(keyword="data analyst")

    try:
        print("🌐 Navigating to ITVIEC login page...")
        driver = spider._init_driver()
        driver.get("https://itviec.com/sign_in")

        # Wait for page to load
        time.sleep(5)

        # Check for Cloudflare challenge indicators
        challenge_selectors = [
            "[class*='cf-challenge']",
            "[class*='cloudflare']",
            ".cf-browser-verification",
            ".cf-challenge-running",
            "[data-ray]",
            ".challenge-form",
            ".captcha",
            "[class*='turnstile']",
            ".cf-turnstile",
            ".h-captcha",
            ".g-recaptcha",
        ]

        challenge_found = False
        for selector in challenge_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and any(elem.is_displayed() for elem in elements):
                    challenge_found = True
                    print(f"⚠️  Cloudflare challenge detected: {selector}")
                    break
            except:
                continue

        if not challenge_found:
            print("✅ No Cloudflare challenge detected!")

            # Try to find login form
            try:
                from selenium.webdriver.common.by import By

                email_input = driver.find_element(
                    By.CSS_SELECTOR, "input[id='user_email']"
                )
                print("✅ Login form is accessible!")
                return True
            except Exception as e:
                print(f"❌ Could not find login form: {e}")
                return False
        else:
            print(
                "🚨 Cloudflare challenge detected - undetected chromedriver may need additional configuration"
            )
            return False

    except Exception as e:
        print(f"❌ Error during Cloudflare detection test: {e}")
        return False

    finally:
        try:
            if hasattr(spider, "driver") and spider.driver:
                spider.driver.quit()
        except:
            pass


if __name__ == "__main__":
    test_itviec_login()
