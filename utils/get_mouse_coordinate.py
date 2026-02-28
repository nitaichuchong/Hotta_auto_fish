from pynput import keyboard
import pyautogui
import tkinter as tk
import threading


class MouseCoordinateTool:
    def __init__(self):
        # 初始化 tkinter 窗口
        self.root = tk.Tk()
        self.root.title("鼠标坐标查看器")

        # 窗口配置（置顶、透明、无边框）
        self.root.attributes("-topmost", True)  # 窗口置顶
        self.root.attributes("-alpha", 0.8)  # 透明度（0.8=80%）
        self.root.overrideredirect(True)  # 隐藏窗口边框/标题栏

        # 坐标显示标签（字体大、清晰）
        self.label = tk.Label(
            self.root,
            text="X: 0, Y: 0",
            font=("微软雅黑", 12, "bold"),
            bg="#000000",  # 黑色背景
            fg="#00FF00",  # 绿色文字（醒目）
            padx=8,
            pady=4,
            bd=0
        )
        self.label.pack()

        # 标记是否运行
        self.running = True

        # 启动鼠标坐标更新线程
        self.update_thread = threading.Thread(target=self.update_coordinates, daemon=True)
        self.update_thread.start()

        # 全局键盘监听
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.keyboard_listener.start()

    def update_coordinates(self):
        """实时更新鼠标坐标"""
        while self.running:
            # 通过 pyautogui 获取鼠标坐标
            x, y = pyautogui.position()

            # 更新标签文字
            self.label.config(text=f"X: {x}, Y: {y}")

            # 实时调整窗口位置跟随鼠标：在鼠标右侧10像素、下方5像素（不遮挡鼠标）
            self.root.geometry(f"+{x + 10}+{y + 5}")

            # 短暂休眠，降低CPU占用
            self.root.after(10, lambda: None)  # 兼容tkinter事件循环
            pyautogui.sleep(0.01)  # 10ms刷新一次，足够实时

    def on_key_press(self, key):
        """全局键盘监听：按 Esc 键退出"""
        try:
            if key == keyboard.Key.esc:  # 监听全局Esc键
                self.quit()
        except Exception:
            pass

    def quit(self, event=None):
        """退出脚本"""
        self.running = False
        self.root.destroy()

    def run(self):
        """启动工具"""
        print("坐标查看工具已启动！")
        print("→ 鼠标移动时会实时显示PyAutoGUI规则的坐标")
        print("→ 按【Esc键】退出工具")
        self.root.mainloop()


if __name__ == "__main__":
    # 禁用 pyautogui 的失败安全（避免鼠标移到左上角触发退出）
    pyautogui.FAILSAFE = False
    # 启动坐标工具
    tool = MouseCoordinateTool()
    tool.run()