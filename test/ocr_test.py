from paddleocr import PaddleOCR

from config import REC_MODEL_PATH, DET_MODEL_PATH

"""
从官方示例改的，直接指定了本地模型路径
"""
ocr = PaddleOCR(
    text_recognition_model_dir=REC_MODEL_PATH,  # 本地识别模型路径
    text_recognition_model_name='PP-OCRv5_mobile_rec',
    text_detection_model_dir=DET_MODEL_PATH,  # 本地检测模型路径
    text_detection_model_name='PP-OCRv5_mobile_det',
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False)

result = ocr.predict(input="./1.png")
for res in result:
    res.print()
    res.save_to_img("output")
    res.save_to_json("output")
