"""配置文件"""
import os

# 这些配置是 PIL 格式用的，可以自行转换
# 钓鱼游戏体力条的区域范围
FISH_GAME_REGION = (648, 50, 1257, 95)
# 钓鱼游戏中鱼的耐力值的区域范围
FISH_ENDURANCE_REGION = (640, 95, 700, 140)

# 项目的根目录
PROJECT_PATH = os.path.dirname(os.getcwd())

# 打包输出目录
DIST_PATH = os.path.join(PROJECT_PATH, "build", "dist")
WORK_PATH = os.path.join(PROJECT_PATH, "build", "work")
SPEC_PATH = os.path.join(PROJECT_PATH, "build")