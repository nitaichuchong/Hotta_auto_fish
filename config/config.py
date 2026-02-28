"""配置文件"""
import os

# 这些配置是 PIL 格式用的，可以自行转换
# 钓鱼游戏体力条的区域范围，比纯体力条范围大点作为容错
FISH_GAME_REGION = (650, 60, 750, 40)
# 钓鱼游戏中鱼的耐力值的区域范围
FISH_ENDURANCE_REGION = (640, 110, 50, 20)

# 所需的黄色像素HSV值上下范围
YELLOW_LOW = (18, 183, 235)
YELLOW_HIGH = (19, 191, 255)

# 钓鱼游戏的体力条范围
# point1 = (670, 70)
# point2 = (1250, 90)
# 钓鱼游戏的耐力值范围
# fish_point1 = (640, 110)
# fish_point2 = (690, 130)

# 项目的根目录
PROJECT_PATH = os.path.dirname(os.getcwd())

# 打包输出目录
DIST_PATH = os.path.join(PROJECT_PATH, "build", "dist")
WORK_PATH = os.path.join(PROJECT_PATH, "build", "work")
SPEC_PATH = os.path.join(PROJECT_PATH, "build")

