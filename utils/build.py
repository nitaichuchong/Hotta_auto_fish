import importlib
import os
import shutil
import sys

from PyInstaller.__main__ import run

from config import PROJECT_PATH, DIST_PATH, WORK_PATH, SPEC_PATH

# 在导入 PaddleOCR 前设置为 True 以跳过模型源链接检查
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
import paddlex


# 获取项目根目录的绝对路径
def get_main_py_path():
    """获取目标的 main 文件在项目中的路径"""
    main_py_path = os.path.join(PROJECT_PATH, "src", "main.py")
    return main_py_path


# 清理旧打包文件（可选）
def clean_old_build():
    """清理旧的打包文件"""
    clean_path = os.path.join(PROJECT_PATH, "build")
    if os.path.exists(clean_path):
        shutil.rmtree(clean_path)


# 核心打包逻辑
def build_exe():
    """建议看 test 里的注释，不写第二遍了"""
    clean_old_build()

    model_source_path = os.path.join(PROJECT_PATH, "models")
    sep = ";" if sys.platform == "win32" else ":"
    target = "./models"
    model_path = f"{model_source_path}{sep}{target}"

    params = [
        get_main_py_path(),  # 你的主程序入口
        "-D",  # 单目录打包
        "-w",  # 无控制台（GUI 程序）
        "--name", "幻塔自动钓鱼",  # 自定义程序名称

        # 添加模型文件
        "--add-data", model_path,

        # PaddleX 相关依赖
        "--collect-data", "paddlex",
        "--collect-binaries", "paddle",

        # PySide6 相关资源（迁移到 Qt 后需要添加）
        "--collect-data", "PySide6",
        "--collect-data", "shiboken6",

        # 官方回答：PyInstaller 无法分析二进制扩展中的导入
        # 因此如果一个模块仅在二进制扩展中导入,我们将无法收集它。
        # 因此,这些模块需要手动指定为隐性导入。
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
