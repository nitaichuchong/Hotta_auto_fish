import sys
import threading
import tkinter as tk
from enum import Enum
from time import sleep

import pyautogui
import pygetwindow as gw

from src.OCR import ocr_init, ocr_recognition
from src.fish_auto import fish_game


class StatusEnum(Enum):
    """
    状态机： INTI 只使用一次，START 和 FINISH 可以互相转换
    """
    INIT = 0
    START = 1
    FINISH = 2


class MainUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("自动钓鱼")
        self.root.geometry("400x400")
        self.root.resizable(False, False)  # 固定窗口的宽度和高度
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # 关闭窗口时的处理
        self.root.attributes("-topmost", True)  # 窗口置顶

        # 创建UI组件
        self.button = None
        self.label = None
        self.status_label = None
        self.endurance_label = None
        self.create_widgets()

        # OCR 实例
        self.ocr = None

        # 线程控制
        self.fish_thread = None
        self.ocr_thread = None
        self.pause_event = threading.Event()  # 暂停事件，True 为暂停
        self.resume_event = threading.Event()  # 用于重新唤醒执行
        self.stop_flag = threading.Event()  # 线程停止标记

        # 控制状态的状态机
        self.status = StatusEnum.INIT

        # 用来标记当前按键状态（用状态机思想控制，清晰并简化按键逻辑）
        self.current_key = None
        self.target_key = None

    def create_widgets(self):
        # 主按钮，将初始化等所有按键通过状态切换集成到一个按钮上
        self.button = tk.Button(
            self.root,
            text="先点此初始化",
            command=self.toggle_button,
            width=10,
        )
        self.button.grid(row=0, column=0, padx=10, pady=20)

        # 基础状态标签
        self.label = tk.Label(
            self.root,
            text="尚未初始化",
            width=20,
        )
        self.label.grid(row=0, column=1, padx=10, pady=20)

        # 执行状态提示标签
        self.status_label = tk.Label(
            self.root,
            text="尚未开始执行",
            width=30,
            anchor="center",
            fg="red",
        )
        self.status_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # 耐力值显示标签
        self.endurance_label = tk.Label(
            self.root,
            text="",
            width=30,
            anchor="center",
            fg="blue"
        )
        self.endurance_label.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

        # 脚本操作提示标签
        self.tips_label = tk.Label(
            self.root,
            text="请不要让该程序窗口遮挡住鱼的耐力值和体力条\n"
                 "先初始化，然后第一下挥杆自己点，再点击开始执行\n"
                 "开始执行只有鼠标跟键盘就别乱点了，目前还没兼容",
            width=40,
            anchor="center",
            fg="green",
        )
        self.tips_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def toggle_button(self):
        # 初始化
        if self.status == StatusEnum.INIT:
            # 获取 ocr 实例
            self.ocr = ocr_init()
            self.button.config(text="开始执行")
            self.label.config(text="初始化完毕！")
            self.status_label.config(text="初始化完成，等待执行")
            self.status = StatusEnum.START
        # 初始化完后，启动控制钓鱼和耐力值识别的线程
        elif self.status == StatusEnum.START:
            # 需要先切换到游戏窗口，否则键盘控制会在脚本窗口上执行，无意义

            self.activate_game_window()
            # 检查线程是否存活
            # 若线程未完全退出就再次点击 “开始”，会创建多个控制线程
            if self.fish_thread and self.fish_thread.is_alive():
                self.stop_flag.set()
                self.fish_thread.join(timeout=1)
            if self.ocr_thread and self.ocr_thread.is_alive():
                self.stop_flag.set()
                self.ocr_thread.join(timeout=1)

            # 重置停止标记和事件
            self.stop_flag.clear()
            self.pause_event.clear()
            self.resume_event.clear()

            # 启动钓鱼控制线程
            self.fish_thread = threading.Thread(
                target=fish_game,
                daemon=True,
                # 传递控制事件
                args=(self.pause_event, self.resume_event, self.stop_flag),
            )
            self.fish_thread.start()

            # 启动耐力值识别线程
            self.ocr_thread = threading.Thread(
                target=self.run_ocr,
                daemon=True,
                args=(self.ocr,),
            )
            self.ocr_thread.start()

            # 状态更新
            self.button.config(text="停止执行")
            self.label.config(text="执行中")
            self.status_label.config(text="自动钓鱼中")
            self.status = StatusEnum.FINISH

        # 终止执行，必须把线程全部停止
        elif self.status == StatusEnum.FINISH:
            # 停止线程
            self.stop_flag.set()
            self.resume_event.set()
            self.pause_event.clear()  # 这里应该解除暂停，确保线程能够收到停止标记

            # 等待线程结束
            if self.fish_thread and self.fish_thread.is_alive():
                self.fish_thread.join(timeout=2)
            if self.ocr_thread and self.ocr_thread.is_alive():
                self.ocr_thread.join(timeout=2)

            # 状态更新
            self.button.config(text="再次开始")
            self.label.config(text="已停止")
            self.status_label.config(text="自动钓鱼已停止")
            self.endurance_label.config(text="已停止检测")
            self.status = StatusEnum.START

    def run_ocr(self, ocr):
        while not self.stop_flag.is_set():
            # 若收到暂停信号则等待
            if self.pause_event.is_set():
                # 等待恢复信号
                self.resume_event.wait()
                # 重置恢复信号为 False
                self.resume_event.clear()

            # 执行 ocr 检测，获取耐力值
            ocr_result = ocr_recognition(ocr)
            if ocr_result is not None:
                # 确认不为空后再解包
                fish_endurance, total_endurance = ocr_result
            # 执行标签更新
                self.endurance_label_update(fish_endurance, total_endurance)
                # 立即更新 UI
                self.root.update()

                if fish_endurance == 0:
                    # 设置暂停标记
                    self.pause_event.set()
                    # 执行收杆流程
                    self.rod_recovery_process()
            # 避免循环占用资源过高，且实际游戏也不需要频繁检测
            sleep(1)


    def endurance_label_update(self, endurance1, endurance2):
        """
        执行耐力值显示标签更新
        :param endurance1: 鱼的当前耐力值
        :param endurance2: 鱼的总耐力值
        :return: None
        """
        # 主线程异步更新，子线程直接操作主线程 UI 会引发冲突
        self.root.after(0, lambda: self.endurance_label.config(text=f"{endurance1}/{endurance2}"))

    def rod_recovery_process(self):
        # 确保操作在游戏窗口执行
        self.activate_game_window()

        self.status_label.config(text="正在收杆中...")
        self.root.update()
        pyautogui.press("1")    # 收杆
        sleep(2)  # 收杆耗时
        pyautogui.click()  # 需要点击一下才行

        self.status_label.config(text="正在准备下一杆...")
        self.root.update()
        pyautogui.press("1")  # 按下键盘 1 开始
        sleep(2)  # 开始后会有一个动画时间

        # 清除暂停标记，打开恢复执行
        self.pause_event.clear()
        self.resume_event.set()
        self.root.update()

    def activate_game_window(self):
        # 激活游戏窗口，确保操作在游戏窗口上执行
        try:
            game_window = gw.getWindowsWithTitle("幻塔")[0]
            game_window.activate()
        except IndexError:
            self.status_label.config(text="未找到游戏窗口！")
            return

    def on_close(self):
        """关闭窗口时确保所有线程退出"""
        # 跟终止按钮执行一样的操作
        self.stop_flag.set()
        self.resume_event.set()
        self.pause_event.clear()  # 这里应该解除暂停，确保线程能够收到停止标记

        if self.fish_thread and self.fish_thread.is_alive():
            self.fish_thread.join(timeout=2)
        if self.ocr_thread and self.ocr_thread.is_alive():
            self.ocr_thread.join(timeout=2)

        self.root.destroy()

    def run(self):
        """启动窗口"""
        self.root.mainloop()
