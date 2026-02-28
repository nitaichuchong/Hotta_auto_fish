import sys
import tkinter as tk
from threading import Thread

from test.detect_test import DetectionRunner


class DetectionUI:
    def __init__(self, root):
        self.root = root
        self.root.title("检测逻辑测试")
        self.root.geometry("300x100")
        self.root.resizable(False, False)  # 固定窗口的宽度和高度
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # 关闭窗口时的处理

        self.label = None
        self.button = None

        # 检测运行器实例
        self.runner = DetectionRunner()
        # 检测线程
        self.detect_thread = None

        # 创建UI组件
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

    def on_close(self):
        """关闭窗口时确保终止检测"""
        if self.detect_thread is not None:
            self.runner.stop_detection()
        self.root.destroy()
        sys.exit(0)

