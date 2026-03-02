import os

from config import FISH_ENDURANCE_REGION, REC_MODEL_PATH, DET_MODEL_PATH
from config.config import REC_MODEL_NAME, DET_MODEL_NAME
from src.detect_logic import capture_and_convert

# 在导入 PaddleOCR 前设置为 True 以跳过模型源链接检查
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
from paddleocr import PaddleOCR


def ocr_init():
    """
    进行 paddleocr 初始化，参数含义请参考官方
    :return: ocr 实例
    """
    # 初始化 PaddleOCR，通过懒加载执行
    ocr = PaddleOCR(
        text_recognition_model_dir=REC_MODEL_PATH,  # 本地识别模型路径
        text_recognition_model_name=REC_MODEL_NAME,
        text_detection_model_dir=DET_MODEL_PATH,  # 本地检测模型路径
        text_detection_model_name=DET_MODEL_NAME,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )
    return ocr


def ocr_recognition(ocr):
    """
    通过 OCR 识别指定区域的文字和数字，返回耐力值，
    若返回为 None 则说明未检测或检测失败
    :param ocr: 初始化的 ocr 实例
    :return:
        current_endurance:  剩余的鱼耐力值
        total_endurance:    鱼总共的耐力值
    """
    bgr_frame, _, _, = capture_and_convert(FISH_ENDURANCE_REGION)

    result = ocr.predict(input=bgr_frame)

    # 返回耐力值并作异常处理
    if result and len(result) > 0:
        text_list = result[0]['rec_texts']
        if not text_list:
            return None
        # 检查是否含有分隔符
        endurance_text = text_list[0].strip()
        if '/' not in endurance_text:
            return None
        # 检查是否符合格式
        parts = endurance_text.split('/')
        if len(parts) != 2:
            return None
        # 检查是否有任意一项出错
        current_str = ''.join(filter(str.isdigit, parts[0]))
        total_str = ''.join(filter(str.isdigit, parts[1]))
        if not current_str or not total_str:
            return None
        # 返回耐力值
        try:
            current_endurance = int(current_str)
            total_endurance = int(total_str)
            return current_endurance, total_endurance
        except ValueError:
            return None

    return None
