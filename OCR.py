import re
from time import sleep

import pytesseract
from PIL import ImageGrab

from config import FISH_ENDURANCE_REGION

# 如果你在 Windows 上，需要指定 Tesseract 可执行文件的路径
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
def fish_endurance_recognition(click_event):
    """
    使用 pytesseract 识别对应区域的文字，来判定当前鱼的耐力值，满足判断条件
    则进行操作
    :param click_event: 控制是否收杆钓下一条鱼的 threading.Event()
    """
    region = FISH_ENDURANCE_REGION
    while True:
        image = ImageGrab.grab(bbox=region)
        # 使用 pytesseract 提取文本
        text = pytesseract.image_to_string(image)
        # 正则表达式，匹配如 1/15 这样的信息
        pattern = r'(\d+/\d+)'
        match_text = re.search(pattern, text)

        # 如果不为空则证明正在钓鱼，为空就表示还没开始，不需要进一步操作
        if match_text:
            # 为了分隔出 result[0]，即 1/15 中的 1
            result = match_text.group(0).split('/')
            if result[0] == "0":    # 等于 0 则表示鱼耐力为 0
                click_event.set()   # 循环钓鱼所需的逻辑
                sleep(5)            # 默认循环间隔需要的操作时间

        # 一直循环识别文字很消耗性能，而且游戏内也不需要频繁识别
        sleep(1)