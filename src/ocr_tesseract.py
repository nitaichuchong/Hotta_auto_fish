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
    # Tesseract配置：仅识别 数字 和 /，限定单行文本
    custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789/'

    text_list = pytesseract.image_to_string(preprocessed_frame, config=custom_config).strip()

    return text_list
