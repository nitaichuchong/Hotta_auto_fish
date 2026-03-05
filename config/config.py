"""配置文件"""
import os
import sys


# 动态获取，开发环境和打包后的路径都要适配，否则 ocr 模型路径有问题
def get_project_path():
    # Pyinstall 提供的方法，获取打包后生成的目录
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS)
    else:
        # 非打包情况下，正常返回根目录
        return os.path.dirname(os.getcwd())


# 项目的根目录
PROJECT_PATH = get_project_path()

# 这些配置是 PIL 格式用的，可以自行转换
# 钓鱼游戏体力条的区域范围，比纯体力条范围大点作为容错
FISH_GAME_REGION = (650, 60, 750, 40)
# 钓鱼游戏中鱼的耐力值的区域范围，依旧大一点作容错
FISH_ENDURANCE_REGION = (630, 110, 50, 30)

# 所需的黄色像素HSV值上下范围
YELLOW_LOW = (18, 183, 235)
YELLOW_HIGH = (19, 191, 255)

# 筛选玩家方块白色轮廓的阈值
WHITE_BLOCK_AREA_MIN = 10
WHITE_BLOCK_AREA_MAX = 100
WHITE_BLOCK_SOLIDITY = 0.5

# 执行钓鱼控制的 x 偏移阈值
OFFSET_THRESHOLD = 5

# 钓鱼游戏的体力条范围
point1 = (670, 70)
point2 = (1250, 90)
# 钓鱼游戏的耐力值范围
fish_point1 = (640, 110)
fish_point2 = (690, 130)

# 打包输出目录
DIST_PATH = os.path.join(PROJECT_PATH, "build", "dist")
WORK_PATH = os.path.join(PROJECT_PATH, "build", "work")
SPEC_PATH = os.path.join(PROJECT_PATH, "build")

# 模型选择开关："paddle"或"tesseract"
OCR_TYPE = "tesseract"

# paddleocr 模型目录
# 文字识别模型
REC_MODEL_PATH = os.path.join(PROJECT_PATH, "models", "en_PP-OCRv5_mobile_rec")
REC_MODEL_NAME = "en_PP-OCRv5_mobile_rec"
# 文字检测模型
DET_MODEL_PATH = os.path.join(PROJECT_PATH, "models", "PP-OCRv5_mobile_det")
DET_MODEL_NAME = "PP-OCRv5_mobile_det"

# Tesseract 模型目录
# Tesseract 本地路径
TESSERACT_PATH = os.path.join(PROJECT_PATH, "models", "tesseract")
# Tesseract 语言包路径
TESSDATA_PREFIX = os.path.join(TESSERACT_PATH, "tessdata")
