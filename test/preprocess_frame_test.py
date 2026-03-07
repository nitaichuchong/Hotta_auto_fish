import os

import cv2

from config import OCR_DEBUG, OCR_DEBUG_SAVE_PATH

OCR_DEBUG_IMAGE_COUNT = 0


def preprocess(bgr_frame):
    """
    对图像预处理过程的测试，方便调参数等等
    """

    # 预处理，先转为灰度图
    gray = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(2, 2))
    contrast_enhanced = clahe.apply(gray)

    # 二值化（黑白分割，让文字和背景彻底分离）
    # 自适应阈值二值化，适配轻微光照不均，比全局阈值更鲁棒
    # 你也可以替换为下方注释的OTSU大津法，背景均匀时效果同样好
    thresh = cv2.adaptiveThreshold(
        contrast_enhanced,
        maxValue=255,
        adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        thresholdType=cv2.THRESH_BINARY,
        blockSize=13,  # 奇数，根据你的数字尺寸调整，数字越小值越小
        C=1  # 常数，微调阈值，过滤噪点
    )
    # 备选：OTSU全局自动二值化（背景均匀时用这个更简单）
    # _, thresh = cv2.threshold(contrast_enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 把当前黑底白字 转为 白底黑字
    binary_inverted = cv2.bitwise_not(thresh)

    # 形态学去噪+边缘优化
    # 核尺寸用(2,2)，避免把小尺寸数字腐蚀掉，迭代次数按需调整
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    # 白底黑字场景，用开运算去除背景噪点，闭运算去除文字内部的小黑点，
    # 先开运算去背景噪点，再闭运算修复文字缺口
    final1 = cv2.morphologyEx(binary_inverted, cv2.MORPH_OPEN, kernel, iterations=1)
    final2 = cv2.morphologyEx(final1, cv2.MORPH_CLOSE, kernel, iterations=1)

    # 可选：锐化增强，让文字边缘更锐利（文字模糊时开启）
    # sharpen_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
    # final = cv2.filter2D(final, -1, sharpen_kernel)

    # 调试部分，保存每个步骤的处理结果方便调整参数
    global OCR_DEBUG_IMAGE_COUNT
    if OCR_DEBUG:
        cv2.imwrite(os.path.join(OCR_DEBUG_SAVE_PATH, f"0_bgr_{OCR_DEBUG_IMAGE_COUNT}.png"), bgr_frame)
        cv2.imwrite(os.path.join(OCR_DEBUG_SAVE_PATH, f"1_gray_{OCR_DEBUG_IMAGE_COUNT}.png"), gray)
        cv2.imwrite(os.path.join(OCR_DEBUG_SAVE_PATH, f"2_contrast_enhanced_{OCR_DEBUG_IMAGE_COUNT}.png"),
                    contrast_enhanced)
        cv2.imwrite(os.path.join(OCR_DEBUG_SAVE_PATH, f"3_thresh_{OCR_DEBUG_IMAGE_COUNT}.png"), thresh)
        cv2.imwrite(os.path.join(OCR_DEBUG_SAVE_PATH, f"4_inverted_{OCR_DEBUG_IMAGE_COUNT}.png"), binary_inverted)
        cv2.imwrite(os.path.join(OCR_DEBUG_SAVE_PATH, f"5_final1_{OCR_DEBUG_IMAGE_COUNT}.png"), final1)
        cv2.imwrite(os.path.join(OCR_DEBUG_SAVE_PATH, f"6_final2_{OCR_DEBUG_IMAGE_COUNT}.png"), final2)
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
