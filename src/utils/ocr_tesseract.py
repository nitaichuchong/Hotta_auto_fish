import os

import pytesseract

from config import TESSERACT_PATH, TESSDATA_PREFIX

# 配置 Tesseract（指定本地exe和语言包路径）
pytesseract.pytesseract.tesseract_cmd = os.path.join(TESSERACT_PATH, "tesseract.exe")
os.environ["TESSDATA_PREFIX"] = TESSDATA_PREFIX


def tesseract_ocr_recognition(preprocessed_frame):
    """
    返回文字识别结果
    :param preprocessed_frame: 预处理后的图像
    :return: 文字识别结果
    """
    # Tesseract配置：
    # 使用 LSTM 和传统引擎混合模式
    # 单行文本识别模式，适合短文本
    # 字符白名单：只识别数字和斜杠
    # 不保留词间空格
    # 最小字符置信度 80%，过滤低质量识别
    # 关闭系统字典，避免干扰数字识别
    # 关闭常用词字典，进一步提升准确性
    custom_config = r'''--oem 3 
        --psm 7 
        -c tessedit_char_whitelist=0123456789/
        -c preserve_interword_spaces=0
        -c min_char_conf=80  # 仅保留置信度≥80的字符（过滤低置信度误判）
        -c load_system_dawg=0  # 关闭系统字典（避免字典干扰数字识别）
        -c load_freq_dawg=0'''
    text_list = pytesseract.image_to_string(preprocessed_frame, config=custom_config).strip()

    return text_list
