"""Tesseract OCR 模块

提供 Tesseract OCR 的文字识别功能。
"""
import os

import pytesseract

from config import TESSERACT_PATH, TESSDATA_PREFIX

# 配置 Tesseract（指定本地 exe 和语言包路径）
pytesseract.pytesseract.tesseract_cmd = os.path.join(TESSERACT_PATH, "tesseract.exe")

# 设置 TESSDATA_PREFIX 环境变量，确保在调用 pytesseract 前设置
os.environ["TESSDATA_PREFIX"] = TESSDATA_PREFIX

# # 调试信息：打印实际使用的路径
# print(f"[Tesseract 调试] TESSERACT_PATH: {TESSERACT_PATH}")
# print(f"[Tesseract 调试] TESSDATA_PREFIX: {TESSDATA_PREFIX}")
# print(f"[Tesseract 调试] TESSDATA_PREFIX 是否存在：{os.path.exists(TESSDATA_PREFIX)}")


def tesseract_ocr_recognition(preprocessed_frame) -> str:
    """使用 Tesseract 进行文字识别
    
    Args:
        preprocessed_frame: 预处理后的图像（二值化或灰度图）。
        
    Returns:
        str: 识别出的文字字符串。
    """
    # Tesseract 配置：
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
        -c load_system_dawg=0  # 关闭系统字典（避免字典干扰数字识别）
        -c load_freq_dawg=0'''
    text_list = pytesseract.image_to_string(preprocessed_frame, config=custom_config).strip()

    return text_list
