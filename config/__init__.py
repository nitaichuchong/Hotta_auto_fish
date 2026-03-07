# 游戏区域配置
from .config import FISH_GAME_REGION, FISH_ENDURANCE_REGION
from .config import YELLOW_LOW, YELLOW_HIGH
from .config import WHITE_BLOCK_AREA_MIN, WHITE_BLOCK_AREA_MAX, WHITE_BLOCK_SOLIDITY
from .config import OFFSET_THRESHOLD

# OCR 相关配置
from .config import OCR_TYPE, TESSERACT_PATH, TESSDATA_PREFIX
from .config import REC_MODEL_PATH, DET_MODEL_PATH, REC_MODEL_NAME, DET_MODEL_NAME

# 调试配置
from .config import OCR_DEBUG, OCR_DEBUG_SAVE_PATH

# 项目路径配置
from .config import PROJECT_PATH
from .config import DIST_PATH, WORK_PATH, SPEC_PATH

# 统一导出
__all__ = [
    # 游戏区域配置
    "FISH_GAME_REGION",
    "FISH_ENDURANCE_REGION",
    "YELLOW_LOW",
    "YELLOW_HIGH",
    "WHITE_BLOCK_AREA_MIN",
    "WHITE_BLOCK_AREA_MAX",
    "WHITE_BLOCK_SOLIDITY",
    "OFFSET_THRESHOLD",
    
    # OCR 相关配置
    "OCR_TYPE",
    "TESSERACT_PATH",
    "TESSDATA_PREFIX",
    "REC_MODEL_PATH",
    "DET_MODEL_PATH",
    "REC_MODEL_NAME",
    "DET_MODEL_NAME",
    
    # 调试配置
    "OCR_DEBUG",
    "OCR_DEBUG_SAVE_PATH",

    # 项目路径配置
    "PROJECT_PATH",
    "DIST_PATH",
    "WORK_PATH",
    "SPEC_PATH",
]
