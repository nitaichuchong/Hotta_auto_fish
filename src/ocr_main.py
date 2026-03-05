import cv2

from src.ocr_paddle_ import paddle_ocr_predict, paddle_ocr_init
from src.ocr_tesseract import tesseract_ocr_recognition
from config import FISH_ENDURANCE_REGION, OCR_TYPE
from src.detect_logic import capture_and_convert


def ocr_init():
    """
    为了对齐接口，但目前只有使用 PaddleOCR 时，使用该方法才有实际意义
    :return: 当前使用 PaddleOCR 时返回初始化后的实例，使用 Tesseract 时返回 True，若配置错误则返回 None
    """
    if OCR_TYPE == "tesseract":
        return True
    elif OCR_TYPE == "paddle":
        return paddle_ocr_init()

    return None


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
        bgr_frame = capture_and_convert(FISH_ENDURANCE_REGION)[0]
        if bgr_frame is None:
            return None

        # 预处理，先转为灰度图
        gray = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2GRAY)

        # 高斯模糊（根据实际效果调）
        blur = cv2.GaussianBlur(gray, (3, 3), 0)
        # 自适应高斯阈值二值化，让每个像素根据周围邻域的亮度自动决定阈值，比固定阈值更鲁棒
        thresh = cv2.adaptiveThreshold(
            blur,
            255,  # 最大值（超过阈值的像素设为255）
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  # 邻域权重：高斯加权
            cv2.THRESH_BINARY,  # 阈值类型：二值化
            11,  # 邻域大小（必须是奇数）
            2  # 常数 C：从邻域均值/加权均值中减去这个数（微调阈值）
        )

        # PaddleOCR 需要3通道输入，把二值化后的单通道转回3通道
        if OCR_TYPE == "paddle":
            preprocessed_frame = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
            # PaddleOCR 需要自身实例
            result = paddle_ocr_predict(ocr, preprocessed_frame)
        # Tesseract 可以直接使用
        elif OCR_TYPE == "tesseract":
            preprocessed_frame = thresh
            result = tesseract_ocr_recognition(preprocessed_frame)

        # 检查是否为空值
        if not result or len(result) == 0:
            return None

        print(f"result = {result}")

        # 检查是否含有分隔符
        if '/' not in result:
            return None

        # 检查是否符合格式
        parts = result.split('/')
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
    # 打印异常日志，便于调试
    except (ValueError, IndexError, TypeError, KeyError, AttributeError) as e:
        # 动态获取异常类型
        print(f"{OCR_TYPE} ocr :{type(e).__name__}: {e}")
        return None
