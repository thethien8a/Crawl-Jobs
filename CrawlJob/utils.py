import re
import unicodedata


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
    text = (search_word or '').strip().lower()
    # Loại bỏ dấu tiếng Việt
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    # Chỉ giữ chữ số, chữ cái và khoảng trắng
    text = re.sub(r'[^a-z0-9\s]+', ' ', text)
    # Thu gọn khoảng trắng và nối bằng '+'
    words = [w for w in text.split() if w]
    return "+".join(words)


def encode_ascii_slug(search_word: str, separator: str = '-') -> str:
    """Tạo slug ASCII không dấu, các từ nối bằng `separator` (mặc định '-')
    Ví dụ: 'Phân tích dữ liệu' -> 'phan-tich-du-lieu'
    """
    text = (search_word or '').strip().lower()
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^a-z0-9\s]+', ' ', text)
    words = [w for w in text.split() if w]
    return separator.join(words)


def clean_location(location):
    location = location.replace('\n', '')
    location = location.strip()
    return location

def regex_find_date(text):
    pattern = r"(\d{1,2})/(\d{1,2})/(\d{4})"
    match = re.search(pattern, text)
    if match:
        return match.group(0)

def clean_text_with_tab(text):
    # Loại bỏ các ký tự không mong muốn và khoảng trắng thừa
    cleaned_text = text.replace('\n', '').replace('\t', '').replace('\r', '').strip()
    return cleaned_text