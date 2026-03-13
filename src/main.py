"""主程序模块

提供自动钓鱼系统的主窗口和核心控制逻辑。
"""
import sys
import time
from enum import Enum
from typing import Optional

import pyautogui
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMainWindow, QApplication

from UI.main_window import Ui_MainWindow
from config import OCR_TYPE
from src.utils.window_manager import set_window_topmost, activate_game_window
from src.ocr_main import ocr_init
from src.sub_threads import FishThread, OCRThread
from src.utils.detect_logic import disable_screenshots, enable_screenshots
from src.utils.input_manager import create_input_manager, InputManager


class StatusEnum(Enum):
    """状态枚举类
    
    定义系统运行状态的枚举值，用于状态机控制。
    
    Attributes:
        INIT (int): 初始化状态，仅使用一次
        READY (int): 就绪状态，可以开始执行
        RUNNING (int): 运行状态，正在执行自动钓鱼
    """
    INIT = 0
    READY = 1
    RUNNING = 2


class MainWindow(QMainWindow):
    """主窗口类
    
    实现自动钓鱼系统的 GUI 界面和核心控制逻辑，包括线程管理、状态切换等。
    """
    
    def __init__(self, /):
        """初始化主窗口
        
        设置 UI 界面、初始化 OCR 实例、线程控制变量和输入管理器。
        """
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 使用 Windows API 设置软置顶，类似 tk 的 -topmost 效果
        set_window_topmost(self, is_topmost=True)

        # OCR 实例
        self.ocr_instance: Optional[object] = None

        # 线程控制
        self.fish_thread: Optional[FishThread] = None
        self.ocr_thread: Optional[OCRThread] = None

        # 控制状态的状态机
        self.status: StatusEnum = StatusEnum.INIT

        # 输入管理器实例
        self.input_manager: Optional[InputManager] = None

        # 初始化绑定
        self._connect_signals()

    def _connect_signals(self) -> None:
        """连接信号与槽
        
        绑定按钮点击事件和窗口关闭事件到相应的处理函数。
        """
        # 绑定按钮操作
        self.ui.button.clicked.connect(self.toggle_button)
        # 窗口关闭
        self.closeEvent = self._on_close

    def toggle_button(self) -> None:
        """切换按钮状态
        
        通过状态机处理判断条件和转化，实现单个按钮集成初始化、执行、停止三种操作。
        """
        # 初始化
        if self.status == StatusEnum.INIT:
            # 获取 ocr 实例
            self.ocr_instance = ocr_init()
            self.ui.button.setText("开始执行")
            self.ui.status_label.setText("初始化完毕！")
            self.status = StatusEnum.READY

        # 初始化完成后，启动控制钓鱼和耐力值识别的线程
        elif self.status == StatusEnum.READY:

            # 激活游戏窗口，确保在执行自动钓鱼前游戏窗口处于激活状态，避免输入失效
            activate_game_window("幻塔  ")

            # 启动线程
            self._start_all_threads()

            # 状态更新
            self.ui.button.setText("停止执行")
            self.ui.status_label.setText("执行中")
            self.status = StatusEnum.RUNNING

        elif self.status == StatusEnum.RUNNING:
            # 确保停止所有线程
            self._stop_all_threads()

            # 状态更新
            self.ui.button.setText("再次开始")
            self.ui.status_label.setText("已停止")
            self.status = StatusEnum.READY

    def _start_all_threads(self) -> None:
        """统一启动所有线程
        
        初始化 OCR 实例（如需要），创建并启动 OCR 线程和钓鱼线程，
        绑定信号槽，启用截图和输入管理器。
        """
        # 如果 OCR 实例为空（PaddleOCR 被销毁后），重新初始化
        if not self.ocr_instance:
            self.ocr_instance = ocr_init()

        # 确保 OCR 实例存在后再创建线程
        if self.ocr_instance:
            self.ocr_thread = OCRThread(self.ocr_instance)
            # 绑定子线程的信号到主线程槽函数
            self.ocr_thread.update_endurance.connect(self._update_endurance_label)
            self.ocr_thread.ocr_error.connect(self._show_ocr_error)

            # 启动钓鱼控制线程
            self.fish_thread = FishThread()
            # 绑定子线程的信号到主线程槽函数
            self.fish_thread.update_fishing_status.connect(self._update_fishing_label)
            # 按键控制 - 使用输入管理器
            self.fish_thread.keyUp.connect(self._handle_key_up)
            self.fish_thread.keyDown.connect(self._handle_key_down)
            # 收杆请求绑定
            self.fish_thread.request_reel.connect(self._do_reel_process)
            # 绑定收杆完成信号到 FishThread 的槽函数
            self.fish_thread.reel_finished.connect(self.fish_thread.on_reel_finished)

            # 将 OCR 识别到的耐力值转发给钓鱼线程
            self.ocr_thread.send_current_endurance.connect(self.fish_thread.receive_endurance)

            # 先启动 OCR 线程，确保钓鱼线程能立即接收耐力值
            self.ocr_thread.start()
            self.fish_thread.start()

            # 默认情况下是 False，OCR 线程创建完成后需启动截图
            # 如果在创建线程前就启动截图，可能会出现线程未完全停止但截图已启用的情况，导致资源冲突和异常
            print("启动截图...")
            enable_screenshots()

            # 初始化输入管理器（默认使用后台模式）
            print("初始化输入管理器（后台模式）...")
            self.input_manager = create_input_manager()

    def _pause_all_threads(self) -> None:
        """统一暂停所有线程
        
        暂停钓鱼线程和 OCR 线程的执行。
        """
        if self.fish_thread:
            self.fish_thread.pause()
        if self.ocr_thread:
            self.ocr_thread.pause()

    def _resume_all_threads(self) -> None:
        """统一恢复所有线程
        
        恢复钓鱼线程和 OCR 线程的执行。
        """
        if self.fish_thread:
            self.fish_thread.resume()
        if self.ocr_thread:
            self.ocr_thread.resume()

    def _stop_all_threads(self) -> None:
        """统一停止所有线程
        
        禁用截图，停止并清理 OCR 线程、钓鱼线程、PaddleOCR 实例和输入管理器，
        确保所有资源完全释放。
        """
        print("=== 开始停止所有线程 ===")

        # 首先禁用截图，防止新的截图请求
        print("禁用截图...")
        disable_screenshots()

        try:
            # 先停止 OCR 线程，因为它不依赖其他线程
            if self.ocr_thread:
                print("正在停止 OCR 线程...")
                self.ocr_thread.stop()
                # 等待确保完全退出
                print("等待 OCR 线程退出...")
                self.ocr_thread.wait(2000)
                print("OCR 线程已停止，准备删除...")
                self.ocr_thread.deleteLater()
                self.ocr_thread = None
                print("OCR 线程已清理完毕")
        except Exception as e:
            print(f"停止 OCR 线程时出错：{e}")
            import traceback
            traceback.print_exc()

        try:
            # 再停止钓鱼线程
            if self.fish_thread:
                print("正在停止钓鱼线程...")
                self.fish_thread.stop()
                # 等待确保完全退出
                print("等待钓鱼线程退出...")
                self.fish_thread.wait(2000)
                print("钓鱼线程已停止，准备删除...")
                self.fish_thread.deleteLater()
                self.fish_thread = None
                print("钓鱼线程已清理完毕")
        except Exception as e:
            print(f"停止钓鱼线程时出错：{e}")
            import traceback
            traceback.print_exc()

        try:
            # 关键：PaddleOCR 需要重新初始化，避免底层资源冲突
            # 如果是 PaddleOCR，在停止后销毁实例（PaddleOCR 内部线程池需要完全释放）
            if self.ocr_instance and OCR_TYPE == "paddle":
                print("正在销毁 PaddleOCR 实例...")
                # PaddleOCR 没有显式的 destroy 方法，通过置空帮助 GC 回收
                del self.ocr_instance
                self.ocr_instance = None
                print("PaddleOCR 实例已销毁")
        except Exception as e:
            print(f"Error destroying PaddleOCR instance: {e}")
            import traceback
            traceback.print_exc()

        # 清理输入管理器
        try:
            if self.input_manager:
                print("正在清理输入管理器...")
                # 输入管理器不需要特殊清理操作，直接置空即可
                self.input_manager = None
                print("输入管理器已清理")
        except Exception as e:
            print(f"清理输入管理器失败：{e}")
            import traceback
            traceback.print_exc()

        print("=== 所有线程停止完成 ===")

    def _handle_key_down(self, key: str) -> None:
        """处理按键按下信号
        
        Args:
            key (str): 按键名称，如 'a', 'd', '1' 等。
        """
        if self.input_manager:
            self.input_manager.key_down(key)

    def _handle_key_up(self, key: str) -> None:
        """处理按键松开信号
        
        Args:
            key (str): 按键名称，如 'a', 'd', '1' 等。
        """
        if self.input_manager:
            self.input_manager.key_up(key)

    def _update_endurance_label(self, current: int, total: int) -> None:
        """更新耐力值标签显示
        
        Args:
            current (int): 鱼当前的耐力值。
            total (int): 鱼总共的耐力值。
        """
        self.ui.endurance_label.setText(f"{current}/{total}")

    def _update_fishing_label(self, text: str) -> None:
        """更新钓鱼状态标签显示
        
        Args:
            text (str): 要显示的钓鱼状态文本。
        """
        self.ui.fishing_label.setText(text)

    def _show_ocr_error(self, error_msg: str) -> None:
        """显示 OCR 错误信息
        
        Args:
            error_msg (str): OCR 识别过程中的异常信息。
        """
        self.ui.status_label.setText(error_msg)
        print(f"[OCR 错误] {error_msg}")

    def _do_reel_process(self) -> None:
        """执行收杆流程第一步
        
        检查运行状态，暂停子线程，发送按键信号触发收杆操作。
        """

        # 检查是否仍在 RUNNING 状态
        if self.status != StatusEnum.RUNNING:
            return

        # 收杆触发后立即暂停子线程执行
        self._pause_all_threads()

        self.ui.fishing_label.setText("正在收杆中...")

        # 使用输入管理器发送按键
        if self.input_manager:
            self.input_manager.press_key('1')
        else:
            print("输入管理器未初始化，使用 pyautogui 发送按键")
            pyautogui.press('1')

        QTimer.singleShot(2000, self._reel_step2)

    def _reel_step2(self) -> None:
        """收杆流程第二步
        
        激活游戏窗口，发送鼠标点击信号完成收杆操作。
        """

        # 检查是否仍在 RUNNING 状态
        if self.status != StatusEnum.RUNNING:
            return

        activate_game_window("幻塔  ")
        time.sleep(0.5)  # 确保窗口激活后再执行点击，避免点击失效
        # 使用输入管理器发送鼠标点击
        if self.input_manager:
            self.input_manager.click_mouse()
        else:
            pyautogui.click()

        QTimer.singleShot(1000, self._reel_step3)

    def _reel_step3(self) -> None:
        """收杆流程第三步
        
        准备下一杆钓鱼，发送按键信号。
        """

        # 检查是否仍在 RUNNING 状态
        if self.status != StatusEnum.RUNNING:
            return

        self.ui.fishing_label.setText("正在准备下一杆...")

        # 使用输入管理器发送按键
        if self.input_manager:
            self.input_manager.press_key('1')
        else:
            pyautogui.press('1')

        QTimer.singleShot(2000, self._reel_resume)

    def _reel_resume(self) -> None:
        """完成收杆，恢复子线程执行
        
        发送收杆完成信号，重置线程标记，恢复线程执行。
        """

        # 检查是否仍在 RUNNING 状态
        if self.status != StatusEnum.RUNNING:
            return

        # 发送收杆完成信号，触发标记重置
        self.fish_thread.reel_finished.emit()

        # 收杆操作完成，恢复线程执行
        self._resume_all_threads()

        self.ui.fishing_label.setText("自动钓鱼中")
        self.ui.endurance_label.setText("等待识别中")

    def _on_close(self, event) -> None:
        """处理窗口关闭事件
        
        在窗口关闭前停止所有线程并清理资源。
        
        Args:
            event: 窗口关闭事件对象。
        """
        print("=== 开始关闭窗口 ===")

        try:
            # 先停止所有线程
            print("停止所有线程...")
            self._stop_all_threads()

            print("资源清理完成")

        except Exception as e:
            print(f"关闭窗口时出错：{e}")
            import traceback
            traceback.print_exc()

        print("=== 准备关闭窗口 ===")
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
