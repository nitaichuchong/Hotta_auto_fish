import subprocess
from pathlib import Path

from config import PROJECT_PATH

UI_DIR = Path(PROJECT_PATH) / "UI" / ".ui"
QRC_DIR = Path(PROJECT_PATH) / "UI" / ".qrc"
OUTPUT_DIR = Path(PROJECT_PATH) / "UI"


def open_designer():
    """打开 Qt Designer"""
    try:
        subprocess.run(["pyside6-designer"])
    except Exception as e:
        # 动态获取异常类型
        print(f"error: {type(e).__name__}: {e}")


def get_all_files(directory):
    """使用 Path 对象递归查找文件"""
    return [f for f in Path(directory).rglob('*') if f.is_file()]


def compile_ui():
    """将 .ui 文件编译为 .py"""
    # 确保目录存在，不存在则创建
    UI_DIR.mkdir(parents=True, exist_ok=True)
    ui_file_list = get_all_files(UI_DIR)
    print(f"UI_DIR: {UI_DIR}")
    print(f"ui_file_list: {ui_file_list}")

    for ui_file in ui_file_list:
        print(f"before_ui_file: {ui_file}")
        output_file = OUTPUT_DIR / Path(ui_file.stem).with_suffix(".py")
        print(f"after_output_file: {output_file}")

        try:
            subprocess.run(
                ["pyside6-uic", str(ui_file), "-o", str(output_file)], )
        except Exception as e:
            print(f"error: {type(e).__name__}: {e}")


def compile_qrc():
    """将 .qrc 文件编译为 .py"""
    QRC_DIR.mkdir(parents=True, exist_ok=True)
    qrc_file_list = get_all_files(QRC_DIR)
    print(f"QRC_DIR: {QRC_DIR}")
    print(f"qrc_file_list: {qrc_file_list}")

    for qrc_file in qrc_file_list:
        print(f"before_qrc_file: {qrc_file}")
        output_file = OUTPUT_DIR / Path(qrc_file.stem).with_suffix(".py")
        print(f"after_output_file: {output_file}")

        try:
            subprocess.run(
                ["pyside6-rcc", str(qrc_file), "-o", str(output_file)], )
        except Exception as e:
            print(f"error: {type(e).__name__}: {e}")


if __name__ == '__main__':
    activate_mode = 2
    if activate_mode == 1:
        open_designer()
    elif activate_mode == 2:
        compile_ui()
    elif activate_mode == 3:
        compile_qrc()
    elif activate_mode == 4:
        compile_ui()
        compile_qrc()
