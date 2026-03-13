"""构建模块

提供项目打包构建功能。
"""
import importlib
import os
import shutil
import sys
from typing import List

from PyInstaller.__main__ import run

from config import PROJECT_PATH, DIST_PATH, WORK_PATH, SPEC_PATH, DXGI_CAPTURE_DLL_PATH

# 在导入 PaddleOCR 前设置为 True 以跳过模型源链接检查
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
import paddlex


def get_main_py_path() -> str:
    """获取主程序文件路径
    
    Returns:
        str: src/main.py 的绝对路径。
    """
    main_py_path = os.path.join(PROJECT_PATH, "src", "main.py")
    return main_py_path


def clean_old_build() -> None:
    """清理旧的打包文件
    
    删除 build 目录以便重新打包。
    """
    clean_path = os.path.join(PROJECT_PATH, "build")
    if os.path.exists(clean_path):
        shutil.rmtree(clean_path)


def build_exe() -> None:
    """执行打包操作
    
    使用 PyInstaller 将项目打包为可执行文件。
    """
    clean_old_build()

    model_source_path = os.path.join(PROJECT_PATH, "models")
    dll_source_path = DXGI_CAPTURE_DLL_PATH
    sep = ";" if sys.platform == "win32" else ":"
    model_path = f"{model_source_path}{sep}./models"
    dll_path = f"{dll_source_path}{sep}./"

    params: List[str] = [
        # 打包切记，路径请勿带有中文，例如 pytesseract 就无法正确识别路径中的中文，导致打包后报错
        get_main_py_path(),  # 你的主程序入口
        "-D",  # 单目录打包
        "-w",  # 无控制台（GUI 程序）
        "--name", "HottaAutoFish",  # 自定义程序名称

        # 添加模型文件
        "--add-data", model_path,

        # 添加 DXGI Capture DLL
        "--add-data", dll_path,

        # PaddleX 相关依赖
        "--collect-data", "paddlex",
        "--collect-binaries", "paddle",

        # PySide6 相关资源（迁移到 Qt 后需要添加）
        "--collect-data", "PySide6",
        "--collect-data", "shiboken6",

        # 官方回答：PyInstaller 无法分析二进制扩展中的导入
        # 因此如果一个模块仅在二进制扩展中导入，我们将无法收集它。
        # 因此，这些模块需要手动指定为隐性导入。
        # 解决 chardet 的 mypyc 编译问题（官方建议）
        # chardet 使用了 lagom 框架和 mypyc 编译，需要手动指定
        # 注意：模块名可能因版本不同而变化，如果报错请替换为实际的模块名
        "--hidden-import", "0deeb2fec52624e647be__mypyc",
        "--collect-submodules", "lagom",

        # 可选：如果使用了 Qt 插件，添加以下参数
        # "--collect-submodules", "PySide6.QtSvg",
        # "--collect-submodules", "PySide6.QtSvgWidgets",

        # 自定义输出路径核心参数
        "--distpath", DIST_PATH,  # 最终可执行文件输出路径
        "--workpath", WORK_PATH,  # 临时编译文件路径
        "--specpath", SPEC_PATH,  # spec 文件生成路径

    ]

    user_deps = [dist.metadata["Name"] for dist in importlib.metadata.distributions()]
    deps_all = list(paddlex.utils.deps.BASE_DEP_SPECS.keys())
    deps_need = [dep for dep in user_deps if dep in deps_all]

    for dep in deps_need:
        params += ["--copy-metadata", dep]

    run(params)


if __name__ == "__main__":
    build_exe()
