import os
from time import sleep

from config import FISH_ENDURANCE_REGION, REC_MODEL_PATH, DET_MODEL_PATH
from src.detect_logic import capture_and_convert

# 在导入 PaddleOCR 前设置为 True 以跳过模型源链接检查
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
from paddleocr import PaddleOCR


def ocr_init():
    # 初始化 PaddleOCR，通过懒加载执行
    ocr = PaddleOCR(
        text_recognition_model_dir=REC_MODEL_PATH,  # 本地识别模型路径
        text_recognition_model_name='PP-OCRv5_mobile_rec',
        text_detection_model_dir=DET_MODEL_PATH,  # 本地检测模型路径
        text_detection_model_name='PP-OCRv5_mobile_det',
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )
    return ocr


def ocr_recognition(ocr):
    """通过 OCR 识别指定区域的文字和数字"""
    bgr_frame, _, _, = capture_and_convert(FISH_ENDURANCE_REGION)

    result = ocr.predict(input=bgr_frame)

    if result and len(result) > 0:
        text = result[0]['rec_texts']
        print(text)
        print(type(text))
        print(text[0])
