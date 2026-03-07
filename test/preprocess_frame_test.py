import os

import cv2
import numpy as np

from config import OCR_DEBUG, OCR_DEBUG_SAVE_PATH

OCR_DEBUG_IMAGE_COUNT = 0


def preprocess(bgr_frame):
    """
    对图像预处理过程的测试，方便调参数等等
    """
    h, w = bgr_frame.shape[:2]
    scale = 2
    frame_scaled = cv2.resize(bgr_frame, (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)

    # 预处理，先转为灰度图
    gray = cv2.cvtColor(frame_scaled, cv2.COLOR_BGR2GRAY)

    # 局部对比度增强
    clahe = cv2.createCLAHE(clipLimit=2, tileGridSize=(4, 4))
    contrast_enhanced = clahe.apply(gray)

    # 该方案适合复杂环境下提高下限的情况，在本项目中不如固定阈值方案
    # 自适应阈值（适配光照不均 / 渐变背景），参数针对放大后的小数字优化
    # thresh_adaptive = cv2.adaptiveThreshold(
    #     contrast_enhanced,
    #     maxValue=255,
    #     adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    #     thresholdType=cv2.THRESH_BINARY_INV,
    #     blockSize=11,  # 奇数，数字越小值越小，比原13更适配小尺寸
    #     C=2  # 越大过滤噪点越多，原1的去噪力度不足
    # )

    # 黑白二值化
    _, white_mask = cv2.threshold(
        contrast_enhanced,
        thresh=230,  # 阈值（可调整，比如230/245）
        maxval=255,  # 阈值上限
        type=cv2.THRESH_BINARY_INV
    )

    # # 开运算，去除小噪点
    open_kernel = np.ones((4, 4), np.uint8)
    final1 = cv2.morphologyEx(white_mask, cv2.MORPH_OPEN, open_kernel, iterations=1)
    # # 闭运算，补全缺口
    close_kernel = np.ones((2, 2), np.uint8)
    final2 = cv2.morphologyEx(final1, cv2.MORPH_CLOSE, close_kernel, iterations=1)


    # 调试部分，保存每个步骤的处理结果方便调整参数
    global OCR_DEBUG_IMAGE_COUNT
    if OCR_DEBUG:
        cv2.imwrite(os.path.join(OCR_DEBUG_SAVE_PATH, f"0_bgr_{OCR_DEBUG_IMAGE_COUNT}.png"), bgr_frame)
        cv2.imwrite(os.path.join(OCR_DEBUG_SAVE_PATH, f"1_gray_{OCR_DEBUG_IMAGE_COUNT}.png"), gray)
        cv2.imwrite(os.path.join(OCR_DEBUG_SAVE_PATH, f"2_contrast_enhanced_{OCR_DEBUG_IMAGE_COUNT}.png"),
                    contrast_enhanced)
        cv2.imwrite(os.path.join(OCR_DEBUG_SAVE_PATH, f"3_thresh_{OCR_DEBUG_IMAGE_COUNT}.png"), white_mask)
        cv2.imwrite(os.path.join(OCR_DEBUG_SAVE_PATH, f"4_final1_{OCR_DEBUG_IMAGE_COUNT}.png"), final1)
        cv2.imwrite(os.path.join(OCR_DEBUG_SAVE_PATH, f"5_final2_{OCR_DEBUG_IMAGE_COUNT}.png"), final2)
        OCR_DEBUG_IMAGE_COUNT += 1


# 获取当前文件所在路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 遍历 preprocess_frame 目录下的所有文件
preprocess_dir = os.path.join(current_dir, 'preprocess_frame')
if os.path.exists(preprocess_dir):
    for filename in os.listdir(preprocess_dir):
        file_path = os.path.join(preprocess_dir, filename)
        if os.path.isfile(file_path):
            print(f"找到文件：{file_path}")
            preprocess(cv2.imread(file_path))
