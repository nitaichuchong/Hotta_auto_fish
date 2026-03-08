# HottaAutoFish

一个用于自动执行幻塔游戏中钓鱼小游戏的自动化工具，通过图像识别和模拟键鼠操作，实现全自动钓鱼过程。

## 功能特点

- 🎣 **全自动钓鱼**：自动识别钓鱼游戏界面，控制角色进行钓鱼操作
- ⚡ **智能耐力检测**：实时识别鱼的耐力值，优化收杆时机
- 📱 **直观的UI界面**：提供简洁的操作界面，显示钓鱼状态和耐力值
- 🔄 **循环钓鱼**：自动完成收杆并再次抛竿的循环过程
- 🔧 **可配置性**：通过配置文件调整识别区域和参数
- 📦 **便捷打包**：提供打包脚本，可生成独立可执行文件

## 安装说明

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/HottaAutoFish.git
cd HottaAutoFish
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 安装PaddleOCR（可选）

如果需要使用PaddleOCR作为识别引擎，请执行以下命令：

```bash
# 安装PaddlePaddle
python -m pip install paddlepaddle==3.0.0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
# 安装PaddleOCR
pip install paddleocr
```

## 使用方法

### 1. 运行主程序

**重要：请以管理员身份运行程序，否则无法在游戏中控制键鼠！**

```bash
# 运行主程序
python src/main.py
```

### 2. 操作流程

1. 打开游戏并进入钓鱼界面
2. 运行本程序
3. 点击"开始执行"按钮
4. 程序会自动激活游戏窗口并开始钓鱼
5. 观察UI界面上的状态显示
6. 点击"停止执行"按钮结束钓鱼

### 3. 配置调整

如果需要调整识别区域或其他参数，请修改 `config/config.py` 文件中的相关配置项。关于图像预处理和具体的识别引擎初始化等信息，请到对应模块下调整。

## 项目结构

```
HottaAutoFish/
├── UI/                # UI界面相关文件
│   ├── .ui/           # Qt设计文件
│   ├── __init__.py
│   ├── detect_test_annotation_ui.py
│   └── main_window.py
├── config/            # 配置文件
│   ├── __init__.py
│   └── config.py
├── models/            # OCR模型
│   ├── PP-OCRv5_mobile_det/  # 文字检测模型
│   ├── PP-OCRv5_mobile_rec/  # 文字识别模型
│   ├── en_PP-OCRv5_mobile_rec/  # 英文识别模型
│   └── tesseract/     # Tesseract OCR
├── src/               # 核心源代码
│   ├── utils/         # 工具函数
│   ├── __init__.py
│   ├── detect_logic.py
│   ├── fish_auto.py
│   ├── main.py        # 主程序入口
│   ├── ocr_main.py
│   └── sub_threads.py
├── test/              # 测试文件
├── utils/             # 辅助工具
│   ├── build.py       # 打包脚本
│   └── get_mouse_coordinate.py  # 鼠标坐标获取工具
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## 核心功能模块

### 1. 主程序（src/main.py）

- 提供Qt界面
- 管理钓鱼线程和OCR线程
- 处理用户交互和状态显示

### 2. 钓鱼逻辑（src/fish_auto.py）

- 实现钓鱼游戏的核心逻辑
- 控制按键和鼠标操作
- 处理收杆和抛竿流程

### 3. OCR识别（src/ocr_main.py）

- 支持PaddleOCR和Tesseract两种识别引擎
- 识别鱼的耐力值
- 提供实时反馈

### 4. 窗口管理（src/utils/window_manager.py）

- 激活游戏窗口
- 设置窗口置顶

### 5. 打包工具（utils/build.py）

- 将程序打包为可执行文件
- 处理依赖和模型文件

## 配置说明

### 主要配置项（config/config.py）

| 配置项                    | 说明           | 默认值                           |
| ---------------------- | ------------ | ----------------------------- |
| FISH_GAME_REGION       | 钓鱼游戏体力条区域    | (650, 60, 750, 40)            |
| FISH_ENDURANCE_REGION  | 鱼的耐力值区域      | (640, 115, 50, 20)            |
| YELLOW_LOW/YELLOW_HIGH | 黄色像素HSV范围    | (18, 183, 235)/(19, 191, 255) |
| OFFSET_THRESHOLD       | 执行钓鱼控制的x偏移阈值 | 10                            |
| OCR_TYPE               | OCR引擎选择      | "tesseract"                   |
| OCR_DEBUG              | OCR调试开关      | True                          |

### 如何调整识别区域

1. 运行 `utils/get_mouse_coordinate.py` 获取鼠标位置
2. 根据获取的坐标修改 `config/config.py` 中的区域配置
3. 保存配置并重启程序

## 注意事项

1. **管理员权限**：必须以管理员身份运行程序，否则无法控制游戏
2. **分辨率**：默认配置适用于1920x1080分辨率，其他分辨率需要调整配置
3. **游戏窗口**：确保游戏窗口标题包含"幻塔"二字
4. **OCR引擎**：默认使用Tesseract，如需使用PaddleOCR请安装相关依赖
5. **打包说明**：使用 `utils/build.py` 打包时，请注意PaddleOCR的特殊打包要求

## 故障排除

### 常见问题

1. **无法控制游戏**：请确保以管理员身份运行程序
2. **识别不准确**：调整 `config/config.py` 中的区域配置
3. **程序崩溃**：检查是否安装了所有依赖，特别是PaddleOCR相关依赖

### 调试模式

开启OCR调试模式（`OCR_DEBUG = True`）可以在 `ocr_debug` 目录下查看预处理后的图像，帮助调整识别参数。

## 许可证

本项目采用MIT许可证，详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交Issue和Pull Request，共同改进这个项目！

## 免责声明

本工具仅用于学习和研究目的，请勿用于任何违反游戏规则或法律法规的行为。使用本工具产生的一切后果由使用者自行承担。
