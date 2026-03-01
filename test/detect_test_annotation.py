import cv2
import time

from src.detect_logic import get_yellow_area_range, get_white_block_pos, capture_and_convert


class DetectionRunner:
    def __init__(self):
        self.region_x = None
        self.bgr_frame = None
        self.is_running = False  # 终止标志
        self.annotated_image = None

        # 触发回调函数的状态标记
        self.image_updated = False
        # UI 的回调函数
        self.on_image_updated = None

    def run_detection(self):
        """可终止的检测循环"""
        self.is_running = True

        while self.is_running:  # 用标志控制循环退出
            start_time = time.time()

            # 截图并转换格式
            self.bgr_frame, _, self.region_x = capture_and_convert()

            # 检测目标点位
            yellow_range = get_yellow_area_range()
            white_center_x = get_white_block_pos()

            # 标注检测结果
            if yellow_range is not None:
                # 将绝对坐标转换为相对坐标
                min_x_abs, max_x_abs = yellow_range
                min_x_rel = min_x_abs - self.region_x
                max_x_rel = max_x_abs - self.region_x

                # 左边界：红色竖线
                cv2.line(
                    img=self.bgr_frame,
                    pt1=(int(min_x_rel), 0),
                    pt2=(int(min_x_rel), self.bgr_frame.shape[0]),
                    color=(0, 0, 255),  # BGR: 红色
                    thickness=2
                )
                # 右边界：蓝色竖线
                cv2.line(
                    img=self.bgr_frame,
                    pt1=(int(max_x_rel), 0),
                    pt2=(int(max_x_rel), self.bgr_frame.shape[0]),
                    color=(255, 0, 0),  # BGR: 蓝色
                    thickness=2
                )

            if white_center_x is not None:
                white_center_x_rel = white_center_x - self.region_x
                # 在垂直方向上取中间值
                white_center_y_rel = self.bgr_frame.shape[0] // 2
                # 中心点：绿色实心圆
                cv2.circle(
                    img=self.bgr_frame,
                    center=(int(white_center_x_rel), white_center_y_rel),
                    radius=5,
                    color=(0, 255, 0),  # 绿色
                    thickness=-1  # 实心
                )

            # 仅当未触发过更新时，才标记并调用回调
            if not self.image_updated:
                self.annotated_image = self.bgr_frame
                self.image_updated = True  # 标记为已更新（避免重复触发）
                # 通过回调函数异步通知UI更新（必须通过after避免跨线程操作UI）
                self.on_image_updated()

            # 控制循环间隔1秒
            elapsed_time = time.time() - start_time
            sleep_time = max(0, 1 - elapsed_time)
            time.sleep(sleep_time)

    def stop_detection(self):
        """终止检测循环"""
        self.is_running = False
        self.annotated_image = None
        print("检测已终止")

    def register_image_callback(self, callback):
        self.on_image_updated = callback
