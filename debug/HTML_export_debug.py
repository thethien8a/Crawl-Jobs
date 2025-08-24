#!/usr/bin/env python3
"""
Quick script để xuất HTML ra file HTML_parse
"""

import requests
import os

# URL cần xuất
url = 'https://www.topcv.vn/viec-lam/nhan-vien-kinh-doanh-thi-truong-sales-thu-nhap-upto-25-trieu-ho-tro-an-trua-xang-xe-dien-thoai-tai-ha-noi/1834873.html?ta_source=BoxFeatureJob_LinkDetail'

# Headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'vi,en-US;q=0.9,en;q=0.8',
}

try:
    print(f"🌐 Getting HTML from: {url}")
    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code == 200:
        # Lưu file vào thư mục mà file Python này đang nằm trong
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(script_dir, 'HTML_parse_debug.html')
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)

        print(f"✅ Saved HTML to: {filename}")
        print(f"📄 Size: {len(response.text)} characters")

    else:
        print(f"❌ HTTP Error: {response.status_code}")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n✨ Done!")
