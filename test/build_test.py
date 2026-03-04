import importlib
import os
import shutil
import sys

from PyInstaller.__main__ import run

from config import PROJECT_PATH, DIST_PATH, WORK_PATH, SPEC_PATH

# 在导入 PaddleOCR 前设置为 True 以跳过模型源链接检查
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
import paddlex

# 参照官方的打包示例，从当前 Python 环境已安装的所有包中，筛选出属于 PaddleX 基础依赖列表里的包
# 具体的每句解释建议 AI 再问一遍，写在这里太多了
user_deps = [dist.metadata["Name"] for dist in importlib.metadata.distributions()]
deps_all = list(paddlex.utils.deps.BASE_DEP_SPECS.keys())
deps_need = [dep for dep in user_deps if dep in deps_all]


# 获取项目根目录的绝对路径
def get_test_path():
    """获取目标的 main 文件在项目中的路径
    :return: test: 程序入口文件的绝对路径
    """
    test = os.path.join(PROJECT_PATH, "test", "ocr_init_for_build_test.py")
    return test


# 清理旧打包文件（可选）
def clean_old_build():
    """清理旧的打包文件"""
    clean_path = os.path.join(PROJECT_PATH, "build")
    if os.path.exists(clean_path):
        shutil.rmtree(clean_path)


# 核心打包逻辑
def build_exe():
    # 清理旧文件
    clean_old_build()

    # 模型目录源路径
    model_source_path = os.path.join(PROJECT_PATH, "models")
    # 在 windows 平台和其它平台使用的分隔符不一样，这里用三元运算得到结果
    sep = ";" if sys.platform == "win32" else ":"
    # 这里是打包后的模型目录，即 _internal/models，Pyinstall 只能设置目标目录在临时目录下
    # 这跟 config 配置里的 Pyinstall 提供的 _MEIPASS 有所联系
    target = "./models"
    # 固定格式：源路径 分隔符 目标路径，注意目标路径只能使用相对路径
    model = f"{model_source_path}{sep}{target}"

    print(model)  # 测试时对路径进行确认

    # 定义打包参数（根命令行写法一致，互相转换）
    params = [
        get_test_path(),  # 你的主程序入口
        "-D",  # 单目录打包
        # "-w",  # 无控制台（GUI程序）
        "--name", "幻塔自动钓鱼",  # 自定义程序名称

        # 添加模型文件夹到打包资源中
        "--add-data", model,

        # 官方示例，照着做就是了
        "--collect-data", "paddlex",
        "--collect-binaries", "paddle",

        # 自定义输出路径核心参数
        "--distpath", DIST_PATH,  # 最终可执行文件输出路径
        "--workpath", WORK_PATH,  # 临时编译文件路径
        "--specpath", SPEC_PATH,  # spec文件生成路径
    ]
    # 通过循环在末尾追加需要的参数
    for dep in deps_need:
        params += ["--copy-metadata", dep]

    # 执行打包，这里的 run 请看本文件的 import
    # 实际上与命令行 Pyinstall 后接参数运行在本质上相同
    run(params)


if __name__ == "__main__":
    build_exe()
