from PySide6.QtCore import QThread, Signal, QWaitCondition, QMutex

from src.fish_auto import key_to_press
from src.ocr_main import ocr_recognition


# 通用线程基类
class BaseThread(QThread):
    """基础线程类，提供暂停、恢复、停止功能"""

    def __init__(self):
        super().__init__()
        self._is_paused = False  # 暂停标记（线程内可控）
        self._is_stop = False  # 停止标记
        self._mutex = QMutex()  # 互斥锁，保护共享变量线程安全
        self._pause_cond = QWaitCondition()  # 新增：暂停条件变量（替代轮询）

    def pause(self):
        """暂停线程"""
        self._mutex.lock()
        self._is_paused = True
        self._mutex.unlock()

    def resume(self):
        """恢复线程"""
        self._mutex.lock()
        self._is_paused = False
        self._pause_cond.wakeAll()
        self._mutex.unlock()

    def stop(self):
        """停止线程"""
        self._mutex.lock()
        self._is_stop = True
        self._is_paused = False  # 确保线程在停止后不继续暂停
        self._pause_cond.wakeAll()
        self._mutex.unlock()

    def run(self):
        """子类需重写"""
        pass


class OCRThread(BaseThread):
    """OCR 识别子线程"""
    # 更新耐力值的信号，有两个 int 参数
    update_endurance = Signal(int, int)
    # 向钓鱼控制线程传递耐力值的信号，只需传递当前值
    send_current_endurance = Signal(int)
    # OCR 异常的信号
    ocr_error = Signal(str)

    def __init__(self, ocr_instance):
        super().__init__()
        self.ocr = ocr_instance  # 主函数传入的 OCR 实例

    def run(self):
        super().run()
        while not self._is_stop:
            # 若收到暂停信号则等待（轮询方式）
            while self._is_paused and not self._is_stop:
                self._mutex.lock()
                while self._is_paused and not self._is_stop:
                    self._pause_cond.wait(self._mutex)  # 线程休眠，直到被resume唤醒
                self._mutex.unlock()

            if self._is_stop:
                break

            # 进行异常捕获，并向主线程发送信号传递识别结果
            try:
                ocr_result = ocr_recognition(self.ocr)
                if ocr_result:
                    current, total = ocr_result
                    self.update_endurance.emit(current, total)
                    self.send_current_endurance.emit(current)
                else:
                    # 未识别到时短暂延迟，但不要等太久
                    self.msleep(200)
                    continue
            except Exception as e:
                error_msg = f"OCR recognition error: {e}"
                self.ocr_error.emit(error_msg)
                self.msleep(100)  # 异常时缩短延迟

            # 检测间隔
            self.msleep(500)


class FishThread(BaseThread):
    """钓鱼控制子线程"""
    # 更新钓鱼状态的信号
    update_fishing_status = Signal(str)
    # 控制键盘按键的信号
    keyDown = Signal(str)
    keyUp = Signal(str)
    # 请求收杆，避免子线程操作键鼠和窗口
    request_reel = Signal()
    # 收杆完成信号
    reel_finished = Signal()

    def __init__(self):
        super().__init__()
        # 状态机控制按键操作
        self.current_key = None
        self.target_key = None
        # 存储从 OCR 线程接收到的当前耐力值
        self.current_endurance = -1
        # 标记是否正在收杆流程中，防止重复触发
        self._is_reeling = False

    def receive_endurance(self, endurance: int):
        """接收 OCR 线程传来的耐力值"""
        self.current_endurance = endurance

    def on_reel_finished(self):
        """接收主线程收杆完成信号，重置标记和获取的耐力值"""
        self._is_reeling = False
        self.current_endurance = -1

    def run(self):
        super().run()
        self.update_fishing_status.emit("自动钓鱼中")

        while not self._is_stop:
            # 若收到暂停信号则等待
            self._mutex.lock()
            while self._is_paused and not self._is_stop:
                self._pause_cond.wait(self._mutex)
            self._mutex.unlock()

            if self._is_stop:
                break

            # 耐力值为 0 时触发收杆（但要排除正在收杆的情况）
            if self.current_endurance == 0 and not self._is_reeling:
                self._is_reeling = True  # 标记正在收杆
                # 发送收杆信号执行操作
                self.request_reel.emit()

            try:
                self.target_key = key_to_press()
                
                # 未识别到时延迟缩短到 50ms，提高响应速度
                if not self.target_key:
                    self.msleep(50)
                    continue

                # 只有按键状态变化时才执行操作（避免重复按键或松开）
                if self.target_key != self.current_key:
                    # 松开之前按下的键
                    if self.current_key is not None:
                        self.keyUp.emit(self.current_key)
                    # 按下新的目标键
                    if self.target_key is not None:
                        self.keyDown.emit(self.target_key)

                    # 更新按键状态
                    self.current_key = self.target_key

                    # 若偏移值小到无需控制，则短暂休眠
                    if self.target_key is None:
                        self.msleep(50)  # 缩短到 50ms
            except Exception as e:
                self.msleep(50)  # 缩短到 50ms

        # 退出循环时确保按键已松开
        if self.current_key is not None:
            self.keyUp.emit(self.current_key)
