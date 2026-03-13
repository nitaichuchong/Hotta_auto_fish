"""配置文件模块

提供项目所需的各种配置常量，包括游戏区域、颜色阈值、模型路径等。
"""
import os

from .path_manager import (
    get_project_path,
    get_tesseract_path,
    get_tessdata_prefix,
    get_dxgi_capture_dll_path
)


# 项目的根目录
PROJECT_PATH: str = get_project_path()

# 这些配置是 PIL 格式用的，可以自行转换
# 钓鱼游戏体力条的区域范围，比纯体力条范围大点作为容错
FISH_GAME_REGION: tuple[int, int, int, int] = (650, 60, 750, 40)
# 钓鱼游戏中鱼的耐力值的区域范围，依旧大一点作容错
FISH_ENDURANCE_REGION: tuple[int, int, int, int] = (640, 115, 50, 20)

# 所需的黄色像素 HSV 值上下范围
YELLOW_LOW: tuple[int, int, int] = (18, 183, 235)
YELLOW_HIGH: tuple[int, int, int] = (19, 191, 255)

# 筛选玩家方块白色轮廓的阈值
WHITE_BLOCK_AREA_MIN: int = 10
WHITE_BLOCK_AREA_MAX: int = 100
WHITE_BLOCK_SOLIDITY: float = 0.5

# 执行钓鱼控制的 x 偏移阈值
OFFSET_THRESHOLD: int = 10

# 钓鱼游戏的体力条范围
point1: tuple[int, int] = (670, 70)
point2: tuple[int, int] = (1250, 90)
# 钓鱼游戏的耐力值范围
fish_point1: tuple[int, int] = (640, 115)
fish_point2: tuple[int, int] = (690, 130)

# 打包输出目录
DIST_PATH: str = os.path.join(PROJECT_PATH, "build", "dist")
WORK_PATH: str = os.path.join(PROJECT_PATH, "build", "work")
SPEC_PATH: str = os.path.join(PROJECT_PATH, "build")

# 模型选择开关："paddle"或"tesseract"
OCR_TYPE: str = "tesseract"

# paddleocr 模型目录
# 文字识别模型
REC_MODEL_PATH: str = os.path.join(PROJECT_PATH, "models", "en_PP-OCRv5_mobile_rec")
REC_MODEL_NAME: str = "en_PP-OCRv5_mobile_rec"
# 文字检测模型
DET_MODEL_PATH: str = os.path.join(PROJECT_PATH, "models", "PP-OCRv5_mobile_det")
DET_MODEL_NAME: str = "PP-OCRv5_mobile_det"

# Tesseract 模型目录
# Tesseract 本地路径
TESSERACT_PATH: str = get_tesseract_path()
# Tesseract 语言包路径
TESSDATA_PREFIX: str = get_tessdata_prefix()

# OCR 调试开关，默认关闭
OCR_DEBUG: bool = False  # 开启后可保存预处理后的图像，便于调试
OCR_DEBUG_SAVE_PATH: str = os.path.join(PROJECT_PATH, "ocr_debug")
# 若不存在调试目录则创建
if OCR_DEBUG and not os.path.exists(OCR_DEBUG_SAVE_PATH):
    os.makedirs(OCR_DEBUG_SAVE_PATH)
# 清理调试目录，但不删除文件夹自身
if OCR_DEBUG and os.path.exists(OCR_DEBUG_SAVE_PATH):
    for filename in os.listdir(OCR_DEBUG_SAVE_PATH):
        file_path = os.path.join(OCR_DEBUG_SAVE_PATH, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

# dxgi_capture.dll 的路径
DXGI_CAPTURE_DLL_PATH: str = get_dxgi_capture_dll_path()
USE_BACKGROUND_MODE: bool = False