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
    """主程序"""

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
        self.tips_label = None
        self.create_widgets()

        # OCR 相关
        self.ocr = None
        self.ocr_lock = threading.Lock()  # OCR 线程锁

        # 线程控制
        self.fish_thread = None
        self.ocr_thread = None
        self.pause_event = threading.Event()  # 暂停事件，True 为暂停
        self.resume_event = threading.Event()  # 用于重新唤醒执行
        self.stop_flag = threading.Event()  # 线程停止标记

        # 控制状态的状态机
        self.status = StatusEnum.INIT

    def create_widgets(self):
        """创建 UI 中的所有组件"""
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
                 "先初始化，然后每次开始执行时的挥杆自己点\n"
                 "开始执行后鼠标跟键盘就别乱点了，目前还没兼容",
            width=40,
            anchor="center",
            fg="green",
        )
        self.tips_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def toggle_button(self):
        """通过最简单的状态机处理判断条件和转化，以实现单个按钮集成多个操作，
        分为初始化、执行、停止三种按钮和对应的逻辑，详细的建议直接看里面各自的注释"""
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

            # 先调用方法确保所有旧线程完全退出，然后才继续执行逻辑
            self.stop_all_threads()

            # 重置停止标记和事件
            self.stop_flag.clear()
            self.pause_event.clear()
            self.resume_event.clear()

            # 验证 OCR 实例是否为新实例
            print(f"ocr id = {id(self.ocr)}")

            if self.ocr is None:
                print("ocr 实例已被释放，需再次初始化")
                try:
                    self.ocr = ocr_init()
                    print("OCR实例重新初始化成功")
                except Exception as e:
                    self.status_label.config(text=f"OCR初始化失败：{e}")
                    print(f"OCR初始化失败：{e}")
                    return

            # 启动线程
            self.start_all_threads()

            # 状态更新
            self.button.config(text="停止执行")
            self.label.config(text="执行中")
            self.status_label.config(text="自动钓鱼中")
            self.status = StatusEnum.FINISH

        # 终止执行，必须把线程全部停止
        elif self.status == StatusEnum.FINISH:
            # 确保停止所有线程
            self.stop_all_threads()

            # 状态更新
            self.button.config(text="再次开始")
            self.label.config(text="已停止")
            self.status_label.config(text="自动钓鱼已停止")
            self.endurance_label.config(text="已停止检测")
            self.status = StatusEnum.START

    def start_all_threads(self):
        """将线程启动单独放置，从 toggle_button 中解耦"""
        # 启动钓鱼控制线程
        self.fish_thread = threading.Thread(
            target=fish_game,
            daemon=True,
            # 传递控制事件
            args=(self.pause_event, self.resume_event, self.stop_flag,),
        )
        self.fish_thread.start()

        # 启动 OCR 线程
        self.ocr_thread = threading.Thread(
            target=self.run_ocr,
            daemon=True,
            args=(self.ocr,),
        )
        self.ocr_thread.start()

    def stop_all_threads(self):
        """
        统一停止所有线程，确保完全退出，
        若线程未完全退出就再次点击 “开始”，会创建多个控制线程，这里先做判断停止这些线程
        """
        if self.stop_flag.is_set():
            return

        print("开始停止所有线程...")

        # 停止所有线程
        self.stop_flag.set()
        self.pause_event.clear()
        self.resume_event.set()  # 先清除暂停标记，再唤醒执行

        # 等待钓鱼控制线程退出
        if self.fish_thread and self.fish_thread.is_alive():
            # 最多等待五秒，进行超时判定是否已退出线程
            self.fish_thread.join(timeout=5)
            if self.fish_thread.is_alive():
                print("钓鱼线程未正常退出，可能残留按键操作")
            else:
                print("钓鱼线程已停止")

        # 等待 OCR 线程退出
        if self.ocr_thread and self.ocr_thread.is_alive():
            self.ocr_thread.join(timeout=1)
            if self.ocr_thread.is_alive():
                print("OCR线程未正常退出")
            else:
                print("OCR线程已停止")

        # 重置线程对象
        self.fish_thread = None
        self.ocr_thread = None

        # 释放 OCR 实例
        self.ocr = None
        print("所有线程已停止，OCR实例已释放")

    def run_ocr(self, ocr):
        """
        持续通过 ocr 进行耐力值检测的子线程，在检测到耐力值为 0 时，会设置暂停标记，
        然后调用收杆操作，直到暂停标记被解除
        :param ocr: 获取的 ocr 实例
        """
        print("OCR线程启动")
        while not self.stop_flag.is_set():
            # 若收到暂停信号则等待
            if self.pause_event.is_set():
                print("OCR线程进入暂停状态")
                # 等待恢复信号
                self.resume_event.wait()
                # 重置恢复信号为 False
                self.resume_event.clear()
                print("OCR线程恢复执行")
                # 再次确认停止标记是否已设置，如已设置直接退出，防止后续逻辑被执行
                if self.stop_flag.is_set():
                    break

            # OCR 识别结果，通过加锁保证单线程执行，同时进行异常捕获
            try:
                with self.ocr_lock:
                    ocr_result = ocr_recognition(ocr)
            except Exception as e:
                print(f"OCR识别异常: {e}")
                ocr_result = None
                sleep(0.2)  # 异常时休眠，避免持续报错
                continue

            if ocr_result is not None:
                # 确认不为空后再解包
                fish_endurance, total_endurance = ocr_result
                # 异步调用，通过主线程更新 UI
                self.root.after(0, self.endurance_label_update, fish_endurance, total_endurance)

                # 耐力值为 0 时收杆
                if fish_endurance == 0:
                    # 设置暂停标记
                    self.pause_event.set()
                    # 执行收杆流程
                    self.root.after(0, self.rod_recovery_process)

            # 避免循环占用资源过高，且实际游戏也不需要频繁检测
            sleep(1)

        print("OCR线程停止")

    def endurance_label_update(self, endurance1, endurance2):
        """
        执行耐力值显示标签更新，该方法被 after 异步更新，如果子线程直接操作主线程 UI 会引发冲突
        :param endurance1: 鱼的当前耐力值
        :param endurance2: 鱼的总耐力值
        """
        self.endurance_label.config(text=f"{endurance1}/{endurance2}")

    def rod_recovery_process(self):
        """
        由于收杆期间每一步操作都可能按下停止执行，并且每一步操作都需要延时来符合游戏实际流程，
        所以将其拆分成多步并用 after 连接，保证作为单线程的 tk 窗口不会被子线程直接操作主线程 UI，
        或是 sleep 导致意外 bug
        """
        # 若已触发停止，直接返回
        if self.stop_flag.is_set():
            return

        # 确保操作在游戏窗口执行
        self.activate_game_window()

        # 此时是在被主线程调用更新 UI ，为安全操作
        self.status_label.config(text="正在收杆中...")

        if not self.stop_flag.is_set():
            pyautogui.press("1")  # 收杆
            # 采用 after 替代 sleep，避免意外的阻塞导致的 bug
            self.root.after(2000, self._continue_recovery)

    def _continue_recovery(self):
        """收杆流程的第二步"""
        if self.stop_flag.is_set():
            return

        pyautogui.click()
        self.root.after(1000, self._finalize_recovery)

    def _finalize_recovery(self):
        """收杆流程的第三步"""
        if self.stop_flag.is_set():
            return

        self.status_label.config(text="正在准备下一杆...")
        pyautogui.press("1")
        self.root.after(2000, self._resume_fishing)

    def _resume_fishing(self):
        """已完成收杆，清除暂停标记，并恢复线程执行"""
        if self.stop_flag.is_set():
            return

        self.pause_event.clear()
        self.resume_event.set()

    def activate_game_window(self):
        """激活游戏窗口，确保操作在游戏窗口上执行"""
        try:
            game_window = gw.getWindowsWithTitle("幻塔")[0]
            game_window.activate()
        except IndexError:
            self.status_label.config(text="未找到游戏窗口！")
            return

    def on_close(self):
        """关闭窗口时确保所有线程退出"""
        # 跟终止按钮执行一样的操作
        self.stop_all_threads()

        self.root.destroy()

    def run(self):
        """启动窗口"""
        self.root.mainloop()
