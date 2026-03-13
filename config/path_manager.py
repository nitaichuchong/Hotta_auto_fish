"""动态路径管理模块

提供统一的动态路径获取功能，兼容开发环境和打包后的环境。
"""
import os
import sys


def get_project_path() -> str:
    """获取项目根目录路径
    
    动态获取项目路径，兼容开发环境和打包后的环境。
    
    Returns:
        str: 项目根目录的绝对路径
    """
    # PyInstaller 提供的方法，获取打包后生成的目录
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS)
    else:
        # 非打包情况下，正常返回根目录
        return os.path.dirname(os.getcwd())


def get_tesseract_path() -> str:
    """获取 Tesseract 可执行文件目录
    
    动态获取 tesseract 目录路径，兼容开发环境和打包后的环境。
    
    Returns:
        str: tesseract 目录的绝对路径
    """
    # PyInstaller 提供的方法，获取打包后生成的目录
    if hasattr(sys, '_MEIPASS'):
        # 打包后，tesseract 在 _internal/models/tesseract 目录下
        return os.path.join(sys._MEIPASS, "models", "tesseract")
    else:
        # 非打包情况下，正常返回当前目录下的路径
        return os.path.join(get_project_path(), "models", "tesseract")


def get_tessdata_prefix() -> str:
    """获取 Tesseract 语言数据目录
    
    动态获取 tessdata 目录路径，兼容开发环境和打包后的环境。
    
    Returns:
        str: tessdata 目录的绝对路径
    """
    # PyInstaller 提供的方法，获取打包后生成的目录
    if hasattr(sys, '_MEIPASS'):
        # 打包后，tessdata 在 _internal/models/tesseract/tessdata 目录下
        return os.path.join(sys._MEIPASS, "models", "tesseract", "tessdata")
    else:
        # 非打包情况下，正常返回当前目录下的路径
        return os.path.join(get_tesseract_path(), "tessdata")


def get_dxgi_capture_dll_path() -> str:
    """获取 DXGI Capture DLL 路径
    
    动态获取 DLL 路径，兼容开发环境和打包后的环境。
    
    Returns:
        str: DLL 的绝对路径
    """
    # PyInstaller 提供的方法，获取打包后生成的目录
    if hasattr(sys, '_MEIPASS'):
        # 打包后，DLL 在 _internal 目录下
        return os.path.join(sys._MEIPASS, "dxgi_capture.dll")
    else:
        # 非打包情况下，正常返回当前目录下的路径
        return os.path.join(get_project_path(), "src", "utils", "dxgi_capture.dll")
