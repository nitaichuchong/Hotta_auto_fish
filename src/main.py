import sys
from enum import Enum

import pyautogui
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMainWindow, QApplication

from UI.main_window import Ui_MainWindow
from config import OCR_TYPE
from src.utils.window_capture import activate_game_window, set_window_topmost
from src.ocr_main import ocr_init
from src.sub_threads import FishThread, OCRThread


class StatusEnum(Enum):
    """
    状态机：INTI 只使用一次，READY 和 RUNNING 可以互相转换
    """
    INIT = 0
    READY = 1
    RUNNING = 2


def _key_up(key):
    """
    槽函数，执行按键操作
    :param key: 需要松开的键
    """
    pyautogui.keyUp(key)


def _key_down(key):
    """
    槽函数，执行按键操作
    :param key: 需要按下的键
    """
    pyautogui.keyDown(key)


class MainWindow(QMainWindow):
    def __init__(self, /):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 使用 Windows API 设置软置顶，类似 tk 的 -topmost 效果
        set_window_topmost(self, is_topmost=True)

        # OCR 实例
        self.ocr_instance = None

        # 线程控制
        self.fish_thread = None
        self.ocr_thread = None

        # 控制状态的状态机
        self.status = StatusEnum.INIT

        # 初始化绑定
        self._connect_signals()

    def _connect_signals(self):
        """信号槽绑定"""
        # 绑定按钮操作
        self.ui.button.clicked.connect(self.toggle_button)
        # 窗口关闭
        self.closeEvent = self._on_close

    def toggle_button(self):
        """
        通过状态机处理判断条件和转化，以实现单个按钮集成多个操作，
        分为初始化、执行、停止三种按钮和对应的逻辑
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
            # 激活游戏窗口
            activate_game_window("幻塔")

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

    def _start_all_threads(self):
        """统一启动所有线程"""
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
            # 按键控制
            self.fish_thread.keyUp.connect(_key_up)
            self.fish_thread.keyDown.connect(_key_down)
            # 收杆请求绑定
            self.fish_thread.request_reel.connect(self._do_reel_process)
            # 绑定收杆完成信号到 FishThread 的槽函数
            self.fish_thread.reel_finished.connect(self.fish_thread.on_reel_finished)

            # 将 OCR 识别到的耐力值转发给钓鱼线程
            self.ocr_thread.send_current_endurance.connect(self.fish_thread.receive_endurance)

            # 先启动 OCR 线程，确保钓鱼线程能立即接收耐力值
            self.ocr_thread.start()
            self.fish_thread.start()

    def _pause_all_threads(self):
        """统一暂停所有线程"""
        if self.fish_thread:
            self.fish_thread.pause()
        if self.ocr_thread:
            self.ocr_thread.pause()

    def _resume_all_threads(self):
        """统一恢复所有线程"""
        if self.fish_thread:
            self.fish_thread.resume()
        if self.ocr_thread:
            self.ocr_thread.resume()

    def _stop_all_threads(self):
        """
        统一停止所有线程，确保所有线程完全退出，
        若未完全退出就再次执行，可能创建多个线程
        """
        # 先停止 OCR 线程，因为它不依赖其他线程
        if self.ocr_thread:
            self.ocr_thread.stop()
            # 等待确保完全退出
            self.ocr_thread.wait(2000)
            self.ocr_thread.deleteLater()
            self.ocr_thread = None

        # 再停止钓鱼线程
        if self.fish_thread:
            self.fish_thread.stop()
            # 等待确保完全退出
            self.fish_thread.wait(2000)
            self.fish_thread.deleteLater()
            self.fish_thread = None

        # 关键：PaddleOCR 需要重新初始化，避免底层资源冲突
        # 如果是 PaddleOCR，在停止后销毁实例（PaddleOCR 内部线程池需要完全释放）
        if self.ocr_instance and OCR_TYPE == "paddle":
            try:
                # PaddleOCR 没有显式的 destroy 方法，通过置空帮助 GC 回收
                del self.ocr_instance
                self.ocr_instance = None
            except Exception as e:
                print(f"Error destroying PaddleOCR instance: {e}")

    def _update_endurance_label(self, current, total):
        """
        槽函数执行 UI 更新
        :param current: 鱼当前的耐力值
        :param total: 鱼总共的耐力值
        """
        self.ui.endurance_label.setText(f"{current}/{total}")

    def _update_fishing_label(self, text):
        """
        槽函数执行 UI 更新
        :param text: label 内更新的字符串
        """
        self.ui.fishing_label.setText(text)

    def _show_ocr_error(self, error_msg):
        """
        槽函数执行 UI 更新
        :param error_msg: OCR 异常信息
        """
        self.ui.status_label.setText(error_msg)

    def _do_reel_process(self):
        """槽函数，执行收杆流程第一步"""

        # 检查是否仍在 RUNNING 状态
        if self.status != StatusEnum.RUNNING:
            return

        # 收杆触发后立即暂停子线程执行
        self._pause_all_threads()

        self.ui.fishing_label.setText("正在收杆中...")
        pyautogui.press('1')
        QTimer.singleShot(2000, self._reel_step2)

    def _reel_step2(self):
        """收杆流程第二步"""

        # 检查是否仍在 RUNNING 状态
        if self.status != StatusEnum.RUNNING:
            return

        pyautogui.click()
        QTimer.singleShot(1000, self._reel_step3)

    def _reel_step3(self):
        """收杆流程第三步"""

        # 检查是否仍在 RUNNING 状态
        if self.status != StatusEnum.RUNNING:
            return

        self.ui.fishing_label.setText("正在准备下一杆...")
        pyautogui.press('1')
        QTimer.singleShot(2000, self._reel_resume)

    def _reel_resume(self):
        """完成收杆，恢复子线程执行"""

        # 检查是否仍在 RUNNING 状态
        if self.status != StatusEnum.RUNNING:
            return

        # 发送收杆完成信号，触发标记重置
        self.fish_thread.reel_finished.emit()

        # 收杆操作完成，恢复线程执行
        self._resume_all_threads()

        self.ui.fishing_label.setText("自动钓鱼中")
        self.ui.endurance_label.setText("等待识别中")

    def _on_close(self, event):
        """窗口关闭事件"""
        self._stop_all_threads()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
