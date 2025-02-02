import sys
import threading
import tkinter as tk

from OCR import fish_endurance_recognition
from fish_auto import fish_game


def main_logic():
    """
    多线程的主要控制逻辑，这里为了方便 tk 窗口管理，将其封装了起来
    """
    # 控制是否收杆钓下一条鱼的事件
    click_event = threading.Event()

    # 启动鱼游戏控制循环
    game_thread = threading.Thread(target=fish_game, args=(click_event,))
    game_thread.daemon = True  # 设置为守护线程，以便主程序退出时自动终止
    game_thread.start()

    # 启动耐力识别线程
    endurance_thread = threading.Thread(target=fish_endurance_recognition, args=(click_event,))
    endurance_thread.daemon = True  # 设置为守护线程
    endurance_thread.start()

def terminate_program():
    """
    tk 窗口中“终止”按钮所执行的逻辑
    """
    # 销毁 tk 窗口并退出程序
    root.destroy()
    # 显式调用exit()可以确保程序完全退出（尽管在守护线程情况下不是必需的）
    sys.exit(0)

def start_program():
    """
    tk 窗口中“开始”按钮所执行的逻辑
    """
    label.config(text="运行中")
    main_logic()

if __name__ == '__main__':
    # 以下主要为 tk 相关代码
    root = tk.Tk()
    root.title("自动钓鱼")

    # 设置开始和终止按钮，并布局
    start_button = tk.Button(root, text="开始", command=start_program)
    terminate_button = tk.Button(root, text="终止", command=terminate_program)
    start_button.grid(row=0, column=2, padx=10, pady=20)
    terminate_button.grid(row=0, column=4, padx=10, pady=20)

    # 创建一个标签用于显示状态信息，初始为空或“未运行”
    label = tk.Label(root, text="未运行", width=20)  # 宽度可以根据需要调整
    label.grid(row=0, column=6, padx=10, pady=20)

    # 设置窗体的固定宽度和高度（以像素为单位）
    root.geometry("300x100")  # 这里300是宽度，100是高度

    # 运行tkinter主循环
    root.mainloop()