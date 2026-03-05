import os

# 在导入 PaddleOCR 前设置为 True 以跳过模型源链接检查
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
from paddleocr import PaddleOCR

from config import REC_MODEL_PATH, REC_MODEL_NAME, DET_MODEL_PATH, DET_MODEL_NAME


def paddle_ocr_init():
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


def paddle_ocr_predict(ocr, preprocessed_frame):
    """
    返回文字识别结果
    :param ocr: PaddleOCR 实例
    :param preprocessed_frame: 预处理后的图像
    :return: 文字识别结果
    """
    result = ocr.predict(input=preprocessed_frame)

    # 检查识别结果是否为空
    if not result or len(result) == 0:
        return None

    # 不为空时才能取出结果
    text_list = result[0]['rec_texts']

    # PaddleOCR 必须再取出 [0] 得到 str 格式， 再通过 strip() 去除开头结尾的空白字符串
    text = result[0].strip()

    return text
