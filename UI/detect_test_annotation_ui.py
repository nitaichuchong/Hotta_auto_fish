import sys
import tkinter as tk
from threading import Thread

import cv2
from PIL import Image, ImageTk

from test.detect_test_annotation import DetectionRunner


class DetectionUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("检测逻辑测试")
        self.root.geometry("800x200")
        self.root.resizable(False, False)  # 固定窗口的宽度和高度
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # 关闭窗口时的处理
        self.root.attributes("-topmost", True)  # 窗口置顶

        # 检测运行器实例
        self.runner = DetectionRunner()
        # 检测线程
        self.detect_thread = None
        # 注册用于更新图片的回调函数
        self.runner.register_image_callback(self._on_image_update_trigger)

        # 创建UI组件
        self.label = None
        self.button = None
        self.image_label = None  # 图片展示的Label组件
        self.update_image_id = None  # 图片更新定时器ID
        self.create_widgets()

    def create_widgets(self):
        """创建按钮和标签"""
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

    def toggle_detection(self):
        """切换开始/终止状态"""
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
                print("线程已置为None")
            self.button.config(text="开始")
            self.label.config(text="已终止")

    def _update_image(self, annotated_image):
        """
        更新 UI 图片，通过回调函数的方式提醒本函数进行更新
        :param annotated_image: 从 self.runner 传回
        :return: None
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

    def _on_image_update_trigger(self):
        """由检测线程触发，异步调用UI更新（避免跨线程操作）"""
        # 用 after 将更新操作放到主线程执行
        self.root.after(0, self._do_update_image)

    def _do_update_image(self):
        """执行图片更新逻辑，并重置状态标记"""
        if self.runner.image_updated:
            # 执行 UI 更新
            self._update_image(self.runner.annotated_image)
            # 重置状态标记
            self.runner.image_updated = False

    def on_close(self):
        """关闭窗口时确保终止检测"""
        if self.detect_thread is not None:
            self.runner.stop_detection()
        self.root.destroy()
        sys.exit(0)

    def run(self):
        """启动窗口"""
        self.root.mainloop()
