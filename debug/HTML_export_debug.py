#!/usr/bin/env python3
"""
Quick script để xuất HTML ra file HTML_parse với Beautiful Soup formatting
"""

import os
import sys

import requests
from bs4 import BeautifulSoup

# URL cần xuất
url = "https://itviec.com/it-jobs/cv-phan-tich-va-thiet-ke-mo-hinh-du-lieu-data-analyst-mb-bank-4214?lab_feature=preview_jd_page"

# Headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "vi,en-US;q=0.9,en;q=0.8",
}

# Fix encoding issue on Windows
if sys.platform == "win32":
    os.system("chcp 65001")

try:
    print(f"[+] Getting HTML from: {url}")
    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code == 200:
        # Parse HTML với Beautiful Soup
        print("[*] Parsing HTML with Beautiful Soup...")
        soup = BeautifulSoup(response.text, "html.parser")

        # Format HTML đẹp hơn
        formatted_html = soup.prettify()

        # Lưu file vào thư mục mà file Python này đang nằm trong
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(script_dir, "HTML_parse_debug.html")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(formatted_html)

        print(f"[+] Saved formatted HTML to: {filename}")
        print(f"[*] Original size: {len(response.text)} characters")
        print(f"[*] Formatted size: {len(formatted_html)} characters")

    else:
        print(f"[!] HTTP Error: {response.status_code}")

except Exception as e:
    print(f"[!] Error: {e}")

print("\n[+] Done!")
