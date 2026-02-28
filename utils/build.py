import os
import shutil

from PyInstaller.__main__ import run

from config.config import PROJECT_PATH, DIST_PATH, WORK_PATH, SPEC_PATH


# 获取项目根目录的绝对路径
def get_main_py_path():
    """获取目标的 main 文件在项目中的路径"""
    main_py_path = os.path.join(PROJECT_PATH, "src", "main.py")
    return main_py_path

# 清理旧打包文件（可选）
def clean_old_build():
    """删除之前打包生成的dist、build目录和.spec文件"""
    # clean_path = [DIST_PATH, WORK_PATH, SPEC_PATH]
    # for path in clean_path:
    #     if os.path.isdir(path):
    #         shutil.rmtree(path)
    #         print(f"removed {path}")
    #     if os.path.isfile(path):
    #         os.remove(path)
    #         print(f"removed {path}")

    clean_path = os.path.join(PROJECT_PATH, "build")
    if os.path.exists(clean_path):
        shutil.rmtree(clean_path)

# 核心打包逻辑
def build_exe():
    # 1. 清理旧文件
    clean_old_build()

    # 2. 定义打包参数（对应命令行参数）
    params = [
        get_main_py_path(),  # 你的主程序入口
        "-D",  # 单目录打包
        "-w",  # 无控制台（GUI程序）
        "--name", "幻塔自动钓鱼",  # 自定义程序名称

        # 自定义输出路径核心参数
        "--distpath", DIST_PATH,  # 最终可执行文件输出路径
        "--workpath", WORK_PATH,  # 临时编译文件路径
        "--specpath", SPEC_PATH,  # spec文件生成路径
    ]

    # 3. 执行打包
    run(params)

    print("打包完成！可执行文件在dist目录下")


if __name__ == "__main__":
    # clean_old_build()
    build_exe()