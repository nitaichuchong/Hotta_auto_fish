import os
import sys
import tkinter as tk

# 在导入 PaddleOCR 前设置为 True 以跳过模型源链接检查
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
from paddleocr import PaddleOCR


# 动态获取程序根目录（兼容开发/打包双环境）
def get_program_root():
    # 判断是否为 Pyinstall 打包后的运行环境
    if hasattr(sys, '_MEIPASS'):
        # 打包后：返回exe文件所在的目录
        return os.path.join(sys._MEIPASS)
    else:
        # 开发环境：返回当前脚本所在的目录（可根据你的项目结构调整）
        return os.path.dirname(os.path.abspath(__file__))


# 拼接路径，彻底替换所有硬编码的绝对路径
root_dir = get_program_root()
project_dir = root_dir

# 文字识别模型
REC_MODEL_PATH = os.path.join(project_dir, "models", "PP-OCRv5_mobile_rec")
REC_MODEL_NAME = "PP-OCRv5_mobile_rec"
# 文字检测模型
DET_MODEL_PATH = os.path.join(project_dir, "models", "PP-OCRv5_mobile_det")
DET_MODEL_NAME = "PP-OCRv5_mobile_det"


def ocr_init():
    print(f"rec_model_dir: {REC_MODEL_PATH}\n"
          f"det_model_dir: {DET_MODEL_PATH}\n"
          f"rec_model_name: {REC_MODEL_NAME}\n"
          f"det_model_name: {DET_MODEL_NAME}\n"
          f"project_dir:{project_dir}")

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


class TestUI:
    def __init__(self):
        """基本上是从主程序的 UI 里复制粘贴来的，只做 ocr 初始化测试"""
        self.root = tk.Tk()
        self.root.title("打包后的UI测试")
        self.root.geometry("400x400")
        self.root.resizable(False, False)  # 固定窗口的宽度和高度
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # 关闭窗口时的处理
        self.root.attributes("-topmost", True)  # 窗口置顶

        self.button = None
        self.create_widgets()

        self.ocr_instance = None

    def on_close(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()

    def create_widgets(self):
        self.button = tk.Button(
            self.root,
            text="点此初始化OCR测试",
            command=self.get_ocr,
            width=20,
            anchor="center",
        )
        self.button.grid(row=0, column=0, padx=10, pady=20)

    def get_ocr(self):
        self.ocr_instance = ocr_init()


if __name__ == "__main__":
    app = TestUI()
    app.run()
