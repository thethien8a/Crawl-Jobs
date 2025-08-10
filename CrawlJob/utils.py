import numpy as np

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

def clean_location(location):
    location = location.replace('\n', '')
    location = location.replace(' ', '')
    return location