"""OCR 识别模块

提供 OCR 初始化、图像预处理和识别结果校验功能。
"""
import traceback
from typing import Optional, Tuple

import cv2
import numpy as np

from src.utils.ocr_paddle_ import paddle_ocr_predict, paddle_ocr_init
from src.utils.ocr_tesseract import tesseract_ocr_recognition
from config import FISH_ENDURANCE_REGION, OCR_TYPE
from src.utils.detect_logic import capture_and_convert

# 调试时用
# OCR_DEBUG_IMAGE_COUNT = 0


def ocr_init() -> Optional[object]:
    """初始化 OCR 实例
    
    根据配置的 OCR 类型初始化相应的 OCR 引擎。PaddleOCR 返回实例，
    Tesseract 返回 True，配置错误返回 None。
    
    Returns:
        Optional[object]: PaddleOCR 实例（使用 PaddleOCR 时），
                         True（使用 Tesseract 时），
                         None（配置错误时）。
    """
    if OCR_TYPE == "tesseract":
        return True
    elif OCR_TYPE == "paddle":
        return paddle_ocr_init()

    return None


def preprocess_frame(bgr_frame: np.ndarray) -> np.ndarray:
    """预处理图像帧
    
    对输入的 BGR 格式图像进行预处理，包括缩放、灰度转换、对比度增强和二值化。
    
    Args:
        bgr_frame (np.ndarray): 输入的 BGR 格式图像。
        
    Returns:
        np.ndarray: 预处理后的二值化图像。
    """
    # 放大图像，让 OCR 识别效果更佳
    h, w = bgr_frame.shape[:2]
    scale = 2
    frame_scaled = cv2.resize(bgr_frame, (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)

    # 预处理，先转为灰度图
    gray = cv2.cvtColor(frame_scaled, cv2.COLOR_BGR2GRAY)

    # 局部对比度增强
    clahe = cv2.createCLAHE(clipLimit=2, tileGridSize=(4, 4))
    contrast_enhanced = clahe.apply(gray)

    # 黑白二值化
    _, white_mask = cv2.threshold(
        contrast_enhanced,
        thresh=235,  # 阈值（可调整，比如 230/245）
        maxval=255,  # 阈值上限
        type=cv2.THRESH_BINARY_INV
    )

    # # 开运算，去除小噪点
    open_kernel = np.ones((2, 2), np.uint8)
    final1 = cv2.morphologyEx(white_mask, cv2.MORPH_OPEN, open_kernel, iterations=1)
    # # 闭运算，补全缺口
    close_kernel = np.ones((1, 1), np.uint8)
    final2 = cv2.morphologyEx(final1, cv2.MORPH_CLOSE, close_kernel, iterations=1)

    return final2


def check_ocr_result(result: str) -> Optional[Tuple[int, int]]:
    """检查 OCR 识别结果是否符合要求
    
    验证识别结果的格式，提取耐力值的当前值和总值。
    
    Args:
        result (str): OCR 识别的原始结果字符串。
        
    Returns:
        Optional[Tuple[int, int]]: (当前耐力值，总耐力值) 的元组，
                                  如果识别结果无效则返回 None。
    """
    # 检查是否为空值
    if not result or len(result) == 0:
        # print(f"{OCR_TYPE} ocr :在第一步校验返回 None")
        return None

    # 检查是否含有分隔符
    if '/' not in result:
        # print(f"{OCR_TYPE} ocr :在第二步校验返回 None")
        return None

    # 检查是否符合格式
    parts = result.split('/')
    if len(parts) != 2:
        # print(f"{OCR_TYPE} ocr :在第三步校验返回 None")
        return None

    # 检查是否有任意一项出错，过滤非数字字符
    current_str = ''.join(filter(str.isdigit, parts[0]))
    total_str = ''.join(filter(str.isdigit, parts[1]))
    if not current_str or not total_str:
        # print(f"{OCR_TYPE} ocr :在第四步校验返回 None")
        return None

    current_endurance = int(current_str)
    total_endurance = int(total_str)

    return current_endurance, total_endurance


def ocr_recognition(ocr: object) -> Optional[Tuple[int, int]]:
    """执行 OCR 识别
    
    捕获指定区域的图像，进行预处理并识别耐力值。
    
    Args:
        ocr (object): 初始化的 OCR 实例（PaddleOCR 模式下需要）。
        
    Returns:
        Optional[Tuple[int, int]]: (当前耐力值，总耐力值) 的元组，
                                  如果识别失败或无有效结果则返回 None。
    """
    # 返回耐力值，用 try 包裹逻辑统一进行异常处理
    try:
        bgr_frame = capture_and_convert(FISH_ENDURANCE_REGION)[0]
        if bgr_frame is None:
            return None

        result = None
        # 对图像进行预处理
        thresh = preprocess_frame(bgr_frame)

        # PaddleOCR 需要 3 通道输入，把二值化后的单通道转回 3 通道
        if OCR_TYPE == "paddle":
            preprocessed_frame = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
            # PaddleOCR 需要自身实例
            result = paddle_ocr_predict(ocr, preprocessed_frame)
        # Tesseract 可以直接使用
        elif OCR_TYPE == "tesseract":
            preprocessed_frame = thresh
            result = tesseract_ocr_recognition(preprocessed_frame)

        # 打印识别结果，便于调试
        # print(f"{OCR_TYPE} ocr :{result}")

        # 检查并返回识别结果
        return check_ocr_result(result)

    # 捕获所有可能的异常，确保函数返回 None 而非崩溃
    # 打印异常日志，便于调试
    except (ValueError, IndexError, TypeError, KeyError, AttributeError) as e:
        # 动态获取异常类型
        print(f"{OCR_TYPE} ocr :{type(e).__name__}: {e}")
        print(f"异常堆栈：{traceback.format_exc()}")
        return None
