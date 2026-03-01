import cv2
import pyautogui
import time
import numpy as np
import os

from src.detect_logic import get_yellow_area_range, get_white_block_pos
from config import FISH_GAME_REGION


class DetectionRunner:
    def __init__(self, region=FISH_GAME_REGION):
        self.region = region
        self.is_running = False  # 终止标志
        self.img_count = 1
        self.save_dir = "detect_result"
        os.makedirs(self.save_dir, exist_ok=True)

    def run_detection(self):
        """可终止的检测循环"""
        self.is_running = True
        print(f"检测结果将保存到 {os.path.abspath(self.save_dir)} 目录下")

        while self.is_running:  # 用标志控制循环退出
            start_time = time.time()

            # 1. 截图并转换格式
            screenshot = pyautogui.screenshot(region=self.region)
            frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            # 2. 检测目标点位
            yellow_range = get_yellow_area_range(self.region)
            white_center_x = get_white_block_pos(self.region)

            # 3. 标注检测结果
            if yellow_range is not None:
                # 将绝对坐标转换为相对坐标
                min_x_abs, max_x_abs = yellow_range
                min_x_rel = min_x_abs - self.region[0]
                max_x_rel = max_x_abs - self.region[0]

                # 左边界：红色竖线
                cv2.line(
                    img=frame,
                    pt1=(int(min_x_rel), 0),
                    pt2=(int(min_x_rel), frame.shape[0]),
                    color=(0, 0, 255),  # BGR: 红色
                    thickness=2
                )
                # 右边界：蓝色竖线
                cv2.line(
                    img=frame,
                    pt1=(int(max_x_rel), 0),
                    pt2=(int(max_x_rel), frame.shape[0]),
                    color=(255, 0, 0),  # BGR: 蓝色
                    thickness=2
                )

            if white_center_x is not None:
                white_center_x_rel = white_center_x - self.region[0]
                # 在垂直方向上取中间值
                white_center_y_rel = frame.shape[0] // 2
                # 中心点：绿色实心圆
                cv2.circle(
                    img=frame,
                    center=(int(white_center_x_rel), white_center_y_rel),
                    radius=5,
                    color=(0, 255, 0),  # 绿色
                    thickness=-1  # 实心
                )

            # 4. 保存标注后的画面
            save_path = os.path.join(self.save_dir, f"{self.img_count}.png")
            cv2.imwrite(save_path, frame)
            print(f"已保存：{save_path}")
            self.img_count += 1

            # 5. 控制循环间隔1秒
            elapsed_time = time.time() - start_time
            sleep_time = max(0, 1 - elapsed_time)
            time.sleep(sleep_time)

    def stop_detection(self):
        """终止检测循环"""
        self.is_running = False
        print("检测已终止")