import os

# 在导入 PaddleOCR 前设置为 True 以跳过模型源链接检查
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

from config import (
    FISH_ENDURANCE_REGION, REC_MODEL_PATH,
    DET_MODEL_PATH, REC_MODEL_NAME, DET_MODEL_NAME)
from src.detect_logic import capture_and_convert
from paddleocr import PaddleOCR


def ocr_init():
    """
    进行 PaddleOCR 初始化，参数含义请参考官方
    :return: 初始化后的 PaddleOCR 实例
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
    通过 OCR 识别指定区域的数字，返回耐力值
    :param ocr: 初始化的 ocr 实例
    :return:
        current_endurance: 剩余的鱼耐力值
        total_endurance: 鱼总共的耐力值
        None: 未检测到有效耐力值/识别过程异常
    """
    # 返回耐力值，用 try 包裹逻辑统一进行异常处理
    try:
        # paddleocr 的支持格式是 BGR
        bgr_frame = capture_and_convert(FISH_ENDURANCE_REGION)[0]

        result = ocr.predict(input=bgr_frame)

        # 返回耐力值并作异常处理
        if not result or len(result) == 0:
            return None

        text_list = result[0]['rec_texts']

        # 检查是否为空值
        if not text_list or len(text_list) == 0:
            return None

        # 检查是否含有分隔符
        endurance_text = text_list[0].strip()
        if '/' not in endurance_text:
            return None

        # 检查是否符合格式
        parts = endurance_text.split('/')
        if len(parts) != 2:
            return None

        # 检查是否有任意一项出错，过滤非数字字符
        current_str = ''.join(filter(str.isdigit, parts[0]))
        total_str = ''.join(filter(str.isdigit, parts[1]))
        if not current_str or not total_str:
            return None

        current_endurance = int(current_str)
        total_endurance = int(total_str)
        return current_endurance, total_endurance

    # 捕获所有可能的异常，确保函数返回 None 而非崩溃
    # 分别打印异常日志，便于调试
    except ValueError as e:
        print(f"OCR ValueError: {e}")
        return None
    except IndexError as e:
        print(f"OCR IndexError: {e}")
        return None
    except TypeError as e:
        print(f"OCR TypeError: {e}")
        return None
    except KeyError as e:
        print(f"OCR KeyError: {e}")
        return None
    except AttributeError as e:
        print(f"OCR AttributeError: {e}")
        return None
