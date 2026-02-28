import cv2
import pyautogui
import time
import numpy as np
import os  # 新增：导入os模块用于目录创建和文件保存

from src.detect_logic import get_yellow_area_range, get_white_block_pos
from config.config import yellow_low, yellow_high
from config.config import FISH_GAME_REGION as region


def test_detection():
    """
    测试检测逻辑：每隔1秒截图并标注检测点位，保存到detect目录（按1、2、3...命名）
    """
    # 新增：创建detect目录（不存在则创建）
    save_dir = "detect_result"
    os.makedirs(save_dir, exist_ok=True)

    # 新增：初始化图片计数器（从1开始）
    img_count = 1

    print("测试脚本已启动！按 'q' 键退出")
    print(f"检测结果将保存到 {os.path.abspath(save_dir)} 目录下")

    while True:
        # 记录循环开始时间，保证每次循环间隔1秒
        start_time = time.time()

        # 1. 截取配置的检测区域画面
        screenshot = pyautogui.screenshot(region=region)
        # 转换为OpenCV可处理的格式（RGB→BGR）
        frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # 2. 调用检测函数获取目标点位
        yellow_range = get_yellow_area_range(region)  # 黄色区域左右边界
        white_center_x = get_white_block_pos(region)  # 白色方块中心点X坐标

        # 3. 在画面上标注检测结果（标注逻辑保持不变）
        # -------- 标注黄色区域边界 --------
        if yellow_range is not None:
            min_x_abs, max_x_abs = yellow_range  # 屏幕绝对坐标
            # 转换为截图内的相对坐标（因为frame是region区域的截图）
            min_x_rel = min_x_abs - region[0]
            max_x_rel = max_x_abs - region[0]

            # 左边界：红色竖线（线宽2）
            cv2.line(
                img=frame,
                pt1=(int(min_x_rel), 0),
                pt2=(int(min_x_rel), frame.shape[0]),
                color=(0, 0, 255),  # BGR: 红色
                thickness=2
            )
            # 右边界：蓝色竖线（线宽2）
            cv2.line(
                img=frame,
                pt1=(int(max_x_rel), 0),
                pt2=(int(max_x_rel), frame.shape[0]),
                color=(255, 0, 0),  # BGR: 蓝色
                thickness=2
            )
            # 标注文字：黄色区域边界坐标
            cv2.putText(
                img=frame,
                text=f"yellow_left: {min_x_abs}",
                org=(10, 30),  # 文字起始位置
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.7,
                color=(0, 0, 255),
                thickness=2
            )
            cv2.putText(
                img=frame,
                text=f"yellow_right: {max_x_abs}",
                org=(10, 60),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.7,
                color=(255, 0, 0),
                thickness=2
            )
        else:
            # 未检测到黄色区域的提示
            cv2.putText(
                img=frame,
                text="None",
                org=(10, 30),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.7,
                color=(0, 255, 255),  # 黄色
                thickness=2
            )

        # -------- 标注白色方块中心点 --------
        if white_center_x is not None:
            # 转换为截图内的相对坐标
            white_center_x_rel = white_center_x - region[0]
            # 垂直方向取截图中间位置（白色方块高度不敏感，取中间更易观察）
            white_center_y_rel = frame.shape[0] // 2

            # 中心点：绿色实心圆（半径5）
            cv2.circle(
                img=frame,
                center=(int(white_center_x_rel), white_center_y_rel),
                radius=5,
                color=(0, 255, 0),  # 绿色
                thickness=-1  # 实心
            )
            # 标注文字：白色方块中心坐标
            cv2.putText(
                img=frame,
                text=f"white_center: {white_center_x:.1f}",
                org=(10, 90),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.7,
                color=(0, 255, 0),
                thickness=2
            )
        else:
            # 未检测到白色方块的提示
            cv2.putText(
                img=frame,
                text="None",
                org=(10, 90),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.7,
                color=(0, 255, 255),
                thickness=2
            )

        # 4. 保存标注后的画面（替换原有的cv2.imshow）
        save_path = os.path.join(save_dir, f"{img_count}.png")
        cv2.imwrite(save_path, frame)
        print(f"已保存：{save_path}")
        img_count += 1  # 计数器递增

        # 5. 控制循环间隔为1秒（扣除已消耗的时间）
        elapsed_time = time.time() - start_time
        sleep_time = max(0, 1 - elapsed_time)  # 避免负数睡眠
        time.sleep(sleep_time)

        # 6. 退出逻辑：按q键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("测试脚本已退出")
            break

    # 释放窗口资源
    cv2.destroyAllWindows()


if __name__ == "__main__":
    test_detection()