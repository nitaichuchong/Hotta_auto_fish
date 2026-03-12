import ctypes

import cv2
import numpy as np
import mss


class MssCaptureManager:
    """
    MSS 截图管理器（非单例），每次使用时临时创建和销毁
    这样可以避免线程安全问题
    """

    def __init__(self):
        print("正在初始化 MssCaptureManager...")
        try:
            # 设置 DPI 感知，确保截图在不同 DPI 设置下正常工作
            try:
                ctypes.windll.user32.SetProcessDPIAware()
                print("DPI 感知设置成功")
            except Exception as e:
                print(f"DPI 感知设置失败：{e}")
            
            # 创建 MSS 实例
            self.mss_instance = mss.mss()
        except Exception as e:
            print(f"MSS 初始化失败：{e}")
            raise

    def capture(self, region=None):
        """
        捕获指定区域图像并返回 BGR 格式的图像
        :param region: 捕获的区域，格式为 (x, y, w, h)
        :type region: tuple
        :return: 捕获的图像（BGR 格式）或 None（捕获失败）
        :rtype: numpy.ndarray or None
        """
        # 安全检查，确保 MSS 实例已创建
        if not hasattr(self, "mss_instance") or self.mss_instance is None:
            print("MSS 实例未创建，无法截图")
            return None

        # 参数校验
        if region is None:
            print("截图区域不能为空")
            return None

        x, y, w, h = region
        
        # 检查区域是否有效
        if any(v < 0 for v in region):
            print(f"无效的截图区域：{region}")
            return None

        try:
            # 定义截图区域
            monitor = {
                "left": x,
                "top": y,
                "width": w,
                "height": h
            }
            
            # 捕获屏幕
            sct_img = self.mss_instance.grab(monitor)
            
            # 转换为 NumPy 数组（BGRA 格式）
            img = np.array(sct_img)
            
            # 转换为 OpenCV 的 BGR 格式（去除 alpha 通道）
            bgr_frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            return bgr_frame
            
        except Exception as e:
            print(f"MSS 截图失败：{e}")
            return None

    def cleanup(self):
        """清理 MSS 资源"""
        if hasattr(self, "mss_instance") and self.mss_instance:
            try:
                self.mss_instance.close()
            except Exception as e:
                print(f"清理 MSS 资源失败：{e}")
            finally:
                self.mss_instance = None


# 提供一个全局获取新实例的函数（每次都会创建新的）
def get_mss_manager():
    """
    获取新的 MSS 截图管理器实例（每次都创建新的）
    :return: MssCaptureManager 实例
    """
    return MssCaptureManager()
