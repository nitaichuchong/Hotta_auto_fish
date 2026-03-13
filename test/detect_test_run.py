"""检测逻辑测试工具

整合了 DetectionRunner 和 DetectionUI 的独立测试脚本，
用于实时观察黄色区域和玩家方块的检测结果。
"""
import sys
import tkinter as tk
from threading import Thread
from typing import Optional

import cv2
from PIL import Image, ImageTk

from src.utils.detect_logic import get_yellow_area_range, get_white_block_pos, capture_and_convert
import time


class DetectionRunner:
    """检测运行器
    
    执行实际的检测逻辑，标注黄色区域和玩家方块位置。
    """

    def __init__(self) -> None:
        """初始化检测运行器
        
        设置截图存储、运行状态标志和回调函数相关变量。
        """
        self.region_x: Optional[int] = None
        self.bgr_frame = None
        self.is_running: bool = False  # 终止标志
        self.annotated_image = None

        # 触发回调函数的状态标记
        self.image_updated: bool = False
        # UI 的回调函数
        self.on_image_updated = None

    def run_detection(self) -> None:
        """执行可终止的检测循环
        
        持续捕获屏幕图像，检测黄色区域和玩家方块位置，
        并在图像上标注结果（红色/蓝色竖线和绿色圆点）。
        """
        self.is_running = True

        while self.is_running:  # 用标志控制循环退出
            start_time = time.time()  # 程序开始执行的时间戳

            # 截图并转换格式
            self.bgr_frame, _, self.region_x = capture_and_convert()
            
            # 检查截图是否成功
            if self.bgr_frame is None:
                # 截图失败，短暂延迟后继续下一次尝试
                time.sleep(0.1)
                continue

            # 检测目标点位
            yellow_range = get_yellow_area_range()
            white_center_x = get_white_block_pos()

            # 标注检测结果
            if yellow_range is not None:
                # 将绝对坐标转换为相对坐标
                min_x_abs, max_x_abs = yellow_range
                min_x_rel = min_x_abs - self.region_x
                max_x_rel = max_x_abs - self.region_x

                # 利用得到的相对坐标，在截图上用 cv2 标注结果
                # pt1 pt2 分别代表绘制起点和终点
                # 左边界：红色竖线
                cv2.line(
                    img=self.bgr_frame,
                    pt1=(int(min_x_rel), 0),  # 意为（x（相对坐标为 0 处），y=0）
                    pt2=(int(min_x_rel), self.bgr_frame.shape[0]),  # （x=0，y=（图像下边界的 y））
                    color=(0, 0, 255),  # BGR: 红色
                    thickness=2  # 线宽为 2
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
                # 得到相对于左边界的 x 坐标
                white_center_x_rel = white_center_x - self.region_x
                # 在垂直方向上取中间值
                white_center_y_rel = self.bgr_frame.shape[0] // 2
                # 中心点：绿色实心圆
                cv2.circle(
                    img=self.bgr_frame,
                    center=(int(white_center_x_rel), white_center_y_rel),
                    radius=5,  # 半径
                    color=(0, 255, 0),  # 绿色
                    thickness=-1  # 实心
                )

            # 仅当未触发过更新时，才标记并调用回调
            if not self.image_updated:
                self.annotated_image = self.bgr_frame
                self.image_updated = True  # 标记为已更新（避免重复触发）
                # 通过回调函数异步通知 UI 更新（必须通过 after 避免跨线程操作 UI）
                self.on_image_updated()

            # 控制循环间隔 1 秒
            elapsed_time = time.time() - start_time  # 当前时间戳 - 开始时间戳，得到程序运行时间
            sleep_time = max(0, 1 - elapsed_time)  # 精准控制运行间隔共 1 秒
            time.sleep(sleep_time)

    def stop_detection(self) -> None:
        """终止检测循环
        
        停止检测循环并清空标注图像。
        """
        self.is_running = False
        self.annotated_image = None
        print("检测已终止")

    def register_image_callback(self, callback) -> None:
        """注册图像更新回调函数
        
        Args:
            callback: UI 类提供的图像更新回调函数。
        """
        self.on_image_updated = callback


class DetectionUI:
    """检测标注测试 UI 类
    
    提供可视化的检测结果显示界面。
    """

    def __init__(self):
        """初始化检测 UI"""
        self.root = tk.Tk()
        self.root.title("检测逻辑测试")
        self.root.geometry("800x200")
        self.root.resizable(False, False)  # 固定窗口的宽度和高度
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # 关闭窗口时的处理
        self.root.attributes("-topmost", True)  # 窗口置顶

        # 检测运行器实例
        self.runner: DetectionRunner = DetectionRunner()
        # 检测线程
        self.detect_thread: Optional[Thread] = None
        # 注册用于更新图片的回调函数
        self.runner.register_image_callback(self._on_image_update_trigger)

        # 创建 UI 组件
        self.label: Optional[tk.Label] = None
        self.button: Optional[tk.Button] = None
        self.image_label: Optional[tk.Label] = None  # 图片展示的 Label 组件
        self.create_widgets()

    def create_widgets(self) -> None:
        """创建 UI 组件
        
        初始化按钮、标签和图片展示框等界面元素。
        """
        # 开始/终止按钮
        self.button = tk.Button(
            self.root,
            text="开始",
            command=self.toggle_detection,
            width=10
        )
        self.button.grid(row=0, column=0, padx=10, pady=20)

        # 状态标签
        self.label = tk.Label(
            self.root,
            text="未运行",
            width=20
        )
        self.label.grid(row=0, column=1, padx=10, pady=20)

        # 图片展示框，用 label 进行承载
        self.image_label = tk.Label(
            self.root,
            bg="#eeeeee")  # 灰色背景（无图时显示）
        self.image_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        # 初始化空白图片（避免首次显示异常）
        self._update_image(None)

    def toggle_detection(self) -> None:
        """切换检测的运行/终止状态
        
        根据当前状态启动或停止检测线程，并更新 UI 显示。
        """
        if self.detect_thread is None or not self.detect_thread.is_alive():
            # 启动检测
            self.detect_thread = Thread(target=self.runner.run_detection, daemon=True)
            self.detect_thread.start()
            self.button.config(text="终止")
            self.label.config(text="运行中")
        else:
            # 终止检测
            self.runner.stop_detection()
            if self.detect_thread.is_alive():
                self.detect_thread.join(timeout=2)  # 等 2 秒，防止卡死
                self.detect_thread = None
                print("线程已置为 None")
            self.button.config(text="开始")
            self.label.config(text="已终止")

    def _on_image_update_trigger(self) -> None:
        """图像更新回调触发器
        
        将 UI 更新操作调度到主线程执行，避免跨线程操作 UI 组件。
        """
        # 用 after 将更新操作放到主线程执行
        self.root.after(0, self._do_update_image)

    def _do_update_image(self) -> None:
        """执行图片更新逻辑
        
        检查更新标记，如有更新则刷新 UI 显示的图片并重置标记。
        """
        if self.runner.image_updated:
            # 执行 UI 更新
            self._update_image(self.runner.annotated_image)
            # 重置状态标记（标记在子线程内）
            self.runner.image_updated = False

    def _update_image(self, annotated_image) -> None:
        """更新 UI 图片显示
        
        Args:
            annotated_image: 带标注结果的 BGR 格式图像，None 表示清空显示。
        """
        # 初始化时将图片置空
        if annotated_image is None:
            self.image_label.config(image="")
            return

        # 传过来的格式为 BGR，需转换回 RGB，PIL 支持 RGB 格式
        rgb_image = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
        # 转换为 Image 对象并调整图片大小
        pil_image = (Image.fromarray(rgb_image)
                     .resize((750, 40), Image.Resampling.LANCZOS))
        # 转换为 tk 可识别的格式
        tk_image = ImageTk.PhotoImage(pil_image)

        # 保留对 tk_image 的引用，否则可能被回收导致不显示
        self.image_label.tk_image = tk_image
        self.image_label.configure(image=tk_image)

    def on_close(self) -> None:
        """处理窗口关闭事件
        
        确保在窗口关闭前停止检测线程并清理资源。
        """
        if self.detect_thread is not None:
            self.runner.stop_detection()
        self.root.destroy()
        sys.exit(0)

    def run(self) -> None:
        """启动 UI 主循环
        
        进入 Tkinter 消息循环，等待用户交互。
        """
        self.root.mainloop()


def annotation_test():
    """运行检测标注测试"""
    ui = DetectionUI()
    ui.run()


if __name__ == '__main__':
    """检测逻辑测试入口"""
    annotation_test()
