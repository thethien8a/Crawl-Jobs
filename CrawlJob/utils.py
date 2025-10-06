import re
import unicodedata

from selenium.webdriver.chrome.options import Options


import logging
import platform
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
            try:
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
            except subprocess.CalledProcessError:
                # Try alternative registry path (64-bit)
                try:
                    output = subprocess.check_output(
                        r'reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome" /v DisplayVersion',
                        shell=True,
                        stderr=subprocess.DEVNULL
                    ).decode('utf-8')
                    
                    match = re.search(r'DisplayVersion\s+REG_SZ\s+(\d+)\.', output)
                    if match:
                        version = int(match.group(1))
                        logger.info(f"Detected Chrome version: {version}")
                        return version
                except subprocess.CalledProcessError:
                    pass
        
        elif system == "Darwin":  # macOS
            # Check Google Chrome.app version
            try:
                output = subprocess.check_output(
                    ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'],
                    stderr=subprocess.DEVNULL
                ).decode('utf-8')
                
                # Extract major version from "Google Chrome 140.0.7339.208"
                match = re.search(r'Google Chrome (\d+)\.', output)
                if match:
                    version = int(match.group(1))
                    logger.info(f"Detected Chrome version: {version}")
                    return version
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
        
        elif system == "Linux":
            # Try google-chrome command
            try:
                output = subprocess.check_output(
                    ['google-chrome', '--version'],
                    stderr=subprocess.DEVNULL
                ).decode('utf-8')
                
                # Extract major version from "Google Chrome 140.0.7339.208"
                match = re.search(r'Google Chrome (\d+)\.', output)
                if match:
                    version = int(match.group(1))
                    logger.info(f"Detected Chrome version: {version}")
                    return version
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Try chromium-browser as alternative
                try:
                    output = subprocess.check_output(
                        ['chromium-browser', '--version'],
                        stderr=subprocess.DEVNULL
                    ).decode('utf-8')
                    
                    match = re.search(r'Chromium (\d+)\.', output)
                    if match:
                        version = int(match.group(1))
                        logger.info(f"Detected Chromium version: {version}")
                        return version
                except (subprocess.CalledProcessError, FileNotFoundError):
                    pass
        
        # If all methods fail
        logger.warning(f"Could not detect Chrome version on {system}. Will use undetected-chromedriver auto-detection.")
        return None
    
    except Exception as e:
        logger.error(f"Error detecting Chrome version: {e}")
        return None


def encode_input(search_word):
    """Hàm này được sử dụng đễ mã hóa chuỗi đầu vào tìm kiếm thành dạng mong muốn

    Args:
        search_word (str): Chuỗi đầu vào tìm kiếm

    Returns:
        str: Chuỗi đã được mã hóa
    """
    # Tách từ
    text_split = search_word.split()
    text_split = [word.lower() for word in text_split]
    return "-".join(text_split)


def encode_joboko_input(search_word: str) -> str:
    """Tạo slug tìm kiếm cho JobOKO: 'tim-viec-lam-<tukhoa>' dạng ASCII, từ cách nhau bằng '+'.
    Ví dụ: 'Python Developer' -> 'tim-viec-lam-python+developer'
    """
    text = (search_word or "").strip().lower()
    # Loại bỏ dấu tiếng Việt
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    # Chỉ giữ chữ số, chữ cái và khoảng trắng
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    # Thu gọn khoảng trắng và nối bằng '+'
    words = [w for w in text.split() if w]
    return "+".join(words)


def clean_location(location):
    location = location.replace("\n", "")
    location = location.strip()
    return location


def regex_find_date(text):
    pattern = r"(\d{1,2})/(\d{1,2})/(\d{4})"
    match = re.search(pattern, text)
    if match:
        return match.group(0)


def clean_text_with_tab(text):
    # Loại bỏ các ký tự không mong muốn và khoảng trắng thừa
    cleaned_text = text.replace("\n", "").replace("\t", "").replace("\r", "").strip()
    return cleaned_text


def create_stealth_chrome_options(headless=False, window_size="1920,1080"):
    """
    Create Chrome options optimized for stealth and reduced notifications.

    Args:
        headless (bool): Whether to run in headless mode
        window_size (str): Browser window size (format: "width,height")

    Returns:
        Options: Configured Chrome options object
    """
    chrome_options = Options()

    if headless:
        chrome_options.add_argument("--headless")

    # Basic stability options
    stability_options = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
    ]

    # Anti-detection options
    anti_detection_options = [
        "--disable-blink-features=AutomationControlled",
    ]

    # User experience options (reduce notifications)
    ux_options = [
        "--disable-extensions",
        "--disable-plugins",
        "--disable-default-apps",
        "--disable-sync",
        "--disable-translate",
        "--hide-scrollbars",
        "--no-first-run",
        "--disable-prompt-on-repost",
        "--disable-sync-preferences",
        "--password-store=basic",
    ]

    # Security and privacy options
    security_options = [
        "--safebrowsing-disable-auto-update",
        "--disable-backgrounding-occluded-windows",
        "--disable-component-extensions-with-background-pages",
        "--disable-client-side-phishing-detection",
    ]

    # Performance and resource options
    performance_options = [
        "--disable-background-timer-throttling",
        "--disable-renderer-backgrounding",
        "--disable-ipc-flooding-protection",
        "--memory-pressure-off",
        "--max_old_space_size=4096",
    ]

    # Logging and debugging options
    logging_options = [
        "--disable-logging",
        "--log-level=3",
        "--silent",
        "--disable-breakpad",
        "--disable-hang-monitor",
        "--metrics-recording-only",
        "--disable-component-update",
        "--disable-background-networking",
    ]

    # Feature control options
    feature_options = [
        "--disable-features=TranslateUI",
    ]

    # Apply all option groups
    all_options = (
        stability_options
        + anti_detection_options
        + ux_options
        + security_options
        + performance_options
        + logging_options
        + feature_options
    )

    for option in all_options:
        chrome_options.add_argument(option)

    # Anti-detection experimental options
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # Browser configuration
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    chrome_options.add_argument(f"--window-size={window_size}")

    return chrome_options
