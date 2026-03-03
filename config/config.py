"""配置文件"""
import os
import sys


def get_project_path():
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS)
    else:
        # 开发环境：返回当前脚本所在的目录（可根据你的项目结构调整）
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

# paddleocr 模型目录
# 文字识别模型
REC_MODEL_PATH = os.path.join(PROJECT_PATH, "models", "PP-OCRv5_mobile_rec")
REC_MODEL_NAME = "PP-OCRv5_mobile_rec"
# 文字检测模型
DET_MODEL_PATH = os.path.join(PROJECT_PATH, "models", "PP-OCRv5_mobile_det")
DET_MODEL_NAME = "PP-OCRv5_mobile_det"
