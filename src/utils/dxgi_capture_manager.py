import ctypes
import os.path
from ctypes import c_int, c_ubyte, c_void_p, POINTER
import atexit

import cv2
import numpy as np
import win32gui

from config import DXGI_CAPTURE_DLL_PATH


class DxgiCaptureManager:
    """
    DXGI 捕获管理器，用于管理 DLL 和窗口句柄
    """
    # 单例模式
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        单例模式，保证只有一个实例
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        print("正在初始化 DxgiCaptureManager...")
        try:
            # 加载由 C++ 编译的 DLL 工具，目前我找到的方案中 python 无法实现 DXGI 捕获
            print(f"正在加载的 DLL 路径: {DXGI_CAPTURE_DLL_PATH}")
            self.dxgi_capture = ctypes.CDLL(DXGI_CAPTURE_DLL_PATH)
            print("DLL 加载成功")
        except Exception as e:
            print(f"DLL 加载失败: {e}")
            raise

        # 定义函数原型
        self.dxgi_capture.init_capture.argtypes = (c_void_p,)
        self.dxgi_capture.init_capture.restype = None
        self.dxgi_capture.capture_window.argtypes = (POINTER(c_ubyte), c_int, c_int, c_int, c_int)
        self.dxgi_capture.capture_window.restype = POINTER(c_ubyte)
        self.dxgi_capture.cleanup.argtypes = ()
        self.dxgi_capture.cleanup.restype = None

        # 设置 DPI 感知
        try:
            ctypes.windll.user32.SetProcessDPIAware()
            print("DPI 感知设置成功")
        except Exception as e:
            print(f"DPI 感知设置失败: {e}")

        # 获取窗口句柄，请一定注意，幻塔在实际运行后，标题后有两个空格，或一个制表符
        self.hwnd = win32gui.FindWindow(None, "幻塔  ")
        # 这里提供了第二种方法，通过窗口类名获取句柄，如果你觉得标题不靠谱，或是标题有动态变化，请尝试用类名获取
        # 获取窗口类名的方法可以看 test 文件夹下的 window_find_test.py
        # hwnd = win32gui.FindWindow("UnrealWindow", None)
        if not self.hwnd:
            raise ValueError("未找到标题为 '幻塔  ' 的窗口")

        # 初始化捕获
        self.dxgi_capture.init_capture(self.hwnd)

        # 注册退出时清理
        atexit.register(self.cleanup)

    def cleanup(self):
        """清理 DXGI 资源"""
        if hasattr(self, "dxgi_capture") and self.dxgi_capture:
            try:
                print("正在释放 DXGI 资源...")
                self.dxgi_capture.cleanup()
                print("DXGI 资源已释放")
            except Exception as e:
                print(f"清理 DXGI 资源失败：{e}")
            finally:
                # 强制置空，防止重复释放
                self.dxgi_capture = None
                self.hwnd = None

    def capture(self, region=None):
        """
        捕获指定区域图像并返回 BGR 格式的图像
        :param region: 捕获的区域，格式为 (x, y, w, h)
        :type region: tuple
        :return: 捕获的图像（BGR 格式）或 None（捕获失败）
        :rtype: numpy.ndarray or None
        """
        # 新增安全检查，确保 DLL 已加载
        if not hasattr(self, "dxgi_capture") or self.dxgi_capture is None:
            print("DLL 未加载，无法截图")
            return None

        # 参数校验
        if region is None:
            return None

        x, y, w, h = region
        # print(f"正在捕获窗口区域: x={x}, y={y}, width={w}, height={h}")
        # print(f"窗口句柄: {self.hwnd}")

        # 分配缓冲区
        # 4 通道为 RGBA 格式
        buffer = np.zeros((h, w, 4), dtype=np.uint8)
        # 将缓冲区指针转换为 ctypes.POINTER(c_ubyte)，以便传递给 C++ 风格的 API
        buffer_ptr = buffer.ctypes.data_as(POINTER(c_ubyte))

        # 单次捕获，result 仅为指向缓冲区的指针，实际内容已在 buffer_ptr 指向的 buffer 中
        # 这是跟 C++ 有关的写法
        result = self.dxgi_capture.capture_window(buffer_ptr, x, y, w, h)

        if result:
            # 转换为 OpenCV 格式 (BGRA to BGR)
            bgr_frame = cv2.cvtColor(buffer, cv2.COLOR_BGRA2BGR)
            return bgr_frame
        else:
            # print("捕获失败")
            return None


# 提供一个全局获取实例的函数
def get_dxgi_manager():
    return DxgiCaptureManager()
