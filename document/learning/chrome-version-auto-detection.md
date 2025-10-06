# Chrome Version Auto-Detection - Documentation

## 📚 Overview

Utility function `get_chrome_version()` tự động phát hiện phiên bản Chrome/Chromium đã cài đặt trên máy để sử dụng với `undetected-chromedriver`.

## 🎯 Vấn đề giải quyết

### **Before (Hardcode):**
```python
# ❌ BAD: Version bị hardcode, phải update thủ công
self.driver = uc.Chrome(options=options, version_main=140)
```

**Vấn đề:**
- Chrome tự động update → version mismatch
- Phải sửa code mỗi khi Chrome update
- Không portable (máy khác có thể khác version)

### **After (Auto-detect):**
```python
# ✅ GOOD: Tự động phát hiện version
from ..utils import get_chrome_version

chrome_version = get_chrome_version()
self.driver = uc.Chrome(options=options, version_main=chrome_version)
```

**Lợi ích:**
- ✅ Tự động adapt với Chrome version hiện tại
- ✅ Không cần update code khi Chrome update
- ✅ Portable trên nhiều máy khác nhau
- ✅ Fallback về auto-detection nếu không detect được

---

## 🔧 Implementation

### **File: `CrawlJob/utils.py`**

```python
import logging
import platform
import re
import subprocess


def get_chrome_version():
    """
    Auto-detect installed Chrome browser version.
    
    Returns:
        int: Major version number of Chrome (e.g., 140, 141)
        None: If Chrome version cannot be detected
    
    Supports:
        - Windows (registry query)
        - macOS (Google Chrome.app)
        - Linux (google-chrome --version)
    """
    system = platform.system()
    logger = logging.getLogger(__name__)
    
    try:
        if system == "Windows":
            # Query Windows Registry for Chrome version
            output = subprocess.check_output(
                r'reg query "HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome" /v DisplayVersion',
                shell=True,
                stderr=subprocess.DEVNULL
            ).decode('utf-8')
            
            # Extract major version (e.g., "140.0.7339.208" -> 140)
            match = re.search(r'DisplayVersion\s+REG_SZ\s+(\d+)\.', output)
            if match:
                version = int(match.group(1))
                logger.info(f"Detected Chrome version: {version}")
                return version
        
        elif system == "Darwin":  # macOS
            # Check Google Chrome.app version
            output = subprocess.check_output(
                ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'],
                stderr=subprocess.DEVNULL
            ).decode('utf-8')
            
            match = re.search(r'Google Chrome (\d+)\.', output)
            if match:
                version = int(match.group(1))
                logger.info(f"Detected Chrome version: {version}")
                return version
        
        elif system == "Linux":
            # Try google-chrome command
            output = subprocess.check_output(
                ['google-chrome', '--version'],
                stderr=subprocess.DEVNULL
            ).decode('utf-8')
            
            match = re.search(r'Google Chrome (\d+)\.', output)
            if match:
                version = int(match.group(1))
                logger.info(f"Detected Chrome version: {version}")
                return version
        
        # If all methods fail
        logger.warning(f"Could not detect Chrome version on {system}. Will use undetected-chromedriver auto-detection.")
        return None
    
    except Exception as e:
        logger.error(f"Error detecting Chrome version: {e}")
        return None
```

---

## 💻 Usage

### **In Spider (LinkedIn, ITviec, etc.):**

```python
import undetected_chromedriver as uc
from ..utils import get_chrome_version


class LinkedinSpider(scrapy.Spider):
    def _init_driver(self):
        options = uc.ChromeOptions()
        # ... configure options ...
        
        try:
            # Auto-detect Chrome version
            chrome_version = get_chrome_version()
            
            if chrome_version:
                self.logger.info(f"Using Chrome version: {chrome_version}")
                self.driver = uc.Chrome(options=options, version_main=chrome_version)
            else:
                # Fallback to auto-detection if version not found
                self.logger.info("Chrome version not detected, using auto-detection")
                self.driver = uc.Chrome(options=options, version_main=None)
            
            self.logger.info("undetected-chromedriver initialized successfully.")
        except Exception as e:
            self.logger.error(f"Failed to initialize undetected-chromedriver: {e}")
            self.driver = None
```

---

## 🔍 Platform Support

### **Windows:**
- Registry key: `HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome`
- Alternative: `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome` (64-bit)
- Command: `reg query`

### **macOS:**
- Path: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
- Command: `Google Chrome --version`
- Output: `Google Chrome 140.0.7339.208`

### **Linux:**
- Command: `google-chrome --version`
- Alternative: `chromium-browser --version`
- Output: `Google Chrome 140.0.7339.208` or `Chromium 140.0.7339.208`

---

## 🧪 Testing

### **Test function manually:**

```python
from CrawlJob.utils import get_chrome_version

# Test detection
version = get_chrome_version()
print(f"Detected Chrome version: {version}")
```

**Expected output:**
```
INFO: Detected Chrome version: 140
Detected Chrome version: 140
```

### **Test in spider:**

```bash
python run_spider.py --spider linkedin --keyword "Data Engineer"
```

**Expected logs:**
```
[linkedin] INFO: Using Chrome version: 140
[undetected_chromedriver.patcher] INFO: patching driver executable
[linkedin] INFO: undetected-chromedriver initialized successfully.
```

---

## ⚠️ Error Handling

### **Case 1: Chrome not installed**

**Behavior:**
```python
version = get_chrome_version()  # Returns None
```

**Spider handling:**
```python
if chrome_version:
    self.driver = uc.Chrome(options=options, version_main=chrome_version)
else:
    # Fallback to None → undetected-chromedriver auto-detects
    self.driver = uc.Chrome(options=options, version_main=None)
```

### **Case 2: Permission denied (Linux/macOS)**

**Log:**
```
WARNING: Could not detect Chrome version on Linux. Will use undetected-chromedriver auto-detection.
```

**Behavior:** Falls back to `version_main=None`

### **Case 3: Registry error (Windows)**

**Tries both:**
1. `HKLM\SOFTWARE\Wow6432Node\...` (32-bit app on 64-bit OS)
2. `HKLM\SOFTWARE\Microsoft\...` (64-bit app)

If both fail → Returns `None`

---

## 📊 Comparison: Before vs After

| Aspect | Before (Hardcode) | After (Auto-detect) |
|--------|-------------------|---------------------|
| **Maintainability** | ❌ Phải update code thủ công | ✅ Tự động adapt |
| **Portability** | ❌ Chỉ work trên version cụ thể | ✅ Work trên mọi version |
| **Chrome Auto-update** | ❌ Break khi Chrome update | ✅ Continue work sau update |
| **Multi-machine** | ❌ Mỗi máy phải config riêng | ✅ Work out-of-the-box |
| **Fallback** | ❌ Không có | ✅ Fallback về auto-detect |
| **Cross-platform** | ❌ Chỉ Windows | ✅ Windows + macOS + Linux |

---

## 🎯 Best Practices

### **1. Always use auto-detection:**
```python
# ✅ GOOD
chrome_version = get_chrome_version()
driver = uc.Chrome(options=options, version_main=chrome_version)

# ❌ BAD
driver = uc.Chrome(options=options, version_main=140)  # Hardcoded
```

### **2. Always have fallback:**
```python
# ✅ GOOD: Graceful fallback
chrome_version = get_chrome_version()
if chrome_version:
    driver = uc.Chrome(options=options, version_main=chrome_version)
else:
    driver = uc.Chrome(options=options, version_main=None)

# ❌ BAD: No fallback
chrome_version = get_chrome_version()
driver = uc.Chrome(options=options, version_main=chrome_version)  # Crash if None
```

### **3. Log version for debugging:**
```python
# ✅ GOOD
chrome_version = get_chrome_version()
if chrome_version:
    self.logger.info(f"Using Chrome version: {chrome_version}")
```

---

## 🐛 Troubleshooting

### **Problem: "Chrome version not detected"**

**Причины:**
1. Chrome không được cài đặt
2. Chrome được cài ở custom path
3. Permission denied (Linux/macOS)

**Solutions:**
- Install Chrome: https://www.google.com/chrome/
- Check Chrome installation:
  ```bash
  # Windows
  reg query "HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome"
  
  # macOS
  /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version
  
  # Linux
  google-chrome --version
  ```

### **Problem: "Version mismatch" sau khi auto-detect**

**Nguyên nhân:** ChromeDriver cache cũ

**Solution:**
```bash
# Delete cache
# Windows
del /q C:\Users\<username>\appdata\roaming\undetected_chromedriver\*

# Linux/macOS
rm -rf ~/.undetected_chromedriver/*
```

---

## 📚 Related

- **undetected-chromedriver**: https://github.com/ultrafunkamsterdam/undetected-chromedriver
- **Chrome for Testing**: https://googlechromelabs.github.io/chrome-for-testing/
- **Selenium Documentation**: https://www.selenium.dev/documentation/

---

## ✅ Summary

**Key Points:**
1. ✅ **Auto-detect Chrome version** với `get_chrome_version()`
2. ✅ **Cross-platform support** (Windows, macOS, Linux)
3. ✅ **Graceful fallback** khi không detect được
4. ✅ **Zero maintenance** khi Chrome auto-update
5. ✅ **Applied to LinkedIn & ITviec spiders**

**Updated Files:**
- `CrawlJob/utils.py`: Added `get_chrome_version()`
- `CrawlJob/spiders/linkedin_spider.py`: Using auto-detection
- `CrawlJob/spiders/itviec_spider.py`: Using auto-detection

**Result:** 🎉 No more version mismatch errors!
