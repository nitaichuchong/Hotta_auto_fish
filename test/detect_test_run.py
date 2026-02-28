import tkinter as tk

from UI.detect_test_ui import DetectionUI

if __name__ == '__main__':
    root = tk.Tk()
    app = DetectionUI(root)
    root.mainloop()