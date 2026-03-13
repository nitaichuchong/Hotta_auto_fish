# HottaAutoFish - 幻塔自动钓鱼工具

<div align="center">

一个基于图像识别和模拟键鼠操作的幻塔游戏自动钓鱼工具

[![Python Version](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%2010%2B-lightgrey.svg)](https://www.microsoft.com/windows)

</div>

---

# ** <mark>写在最前面</mark>**

**<mark>本文除该部分外其余为AI辅助编写，所以优先看这里，而且希望能认真看完。**</mark>

首先感谢 dxgi 后台捕获的原作者项目：

[https://github.com/wangpy1995/dxgi4py]()

我自己是没有能力编写的，而且内外网上也都没有找到适用的方案，非常感谢该项目，否则关于后台部分无法实现。



### **自动钓鱼操作核心部分：**

    模式有前台和后台两种，可以在 config 配置文件中切换。

    默认方式为前台，即操作需要锁定在游戏窗口上，且游戏窗口在系统中置顶，在开始执行后程序会接管键鼠，不能乱动，除去自行选择开始执行和停止执行外，只能挂机看着它钓鱼，这是前台操作，也是本项目最初的设想和花了最大精力完善的部分。

    后台模式是伪后台，理论上可以直接开始执行后让游戏和程序都放在后台，通过 dxgi 捕获后台画面，以及 win32 API 向游戏发送操作，实现完全挂机。但实际上由于幻塔的钓鱼在钓上后的结算画面，即【点击任意处】会拦截非前台的键鼠操作（包括最底层的系统级 API 操作），所以即便使用后台模式，在收杆时也需要切回游戏画面，来发送【鼠标点击】这一操作来关闭结算画面。我个人认为这算不上完全的后台挂机，虽然不影响在这个过程可以做别的事，但是切回画面的操作会比较频繁，变得意义不大。

    如果你开始执行，并且确定了使用管理员权限运行的话，OCR 能识别鱼的耐力值但键鼠操作未生效，说明键鼠操作没有锁定到游戏窗口上，可以点一下游戏窗口，来将游戏窗口激活为置顶。

### **技术细节解释**

    权限问题非常重要，现代游戏大部分都做了各种脚本操作的拦截，不使用管理员权限是无法通过程序执行键鼠操作的，而使用了 DX11、12 的游戏在后台时，其画面只能用 dxgi 捕获，（前台随意，独占前台的全屏显示 DirectX 渲染不影响对于显示器当前画面的直接截取）具体相关技术和原因，以及游戏的渲染方式和防作弊等安全机制进行的拦截等，可以自行查询相关信息，了解并不难，破解才难

    记住不要最小化，最小化是无法捕捉的，可以直接切换，如 Alt + Tab

    除 dxgi技术外，有其它的后台画面捕获方案，但是基本上都无法捕获 DirectX 渲染。

### **快速上手**

    先看 src/utils 下的基本工具，再看 src 下的 fish_auto 和 ocr_main，main 和 sub_threads 主要是 PySide6 的内容，程序本身的逻辑并不多。

    看完 src 其它就随意了，也可以结合源码看 ocr_debug 下预处理图像的过程示例，这是调试得最有意思的一部分。

    



下方全为AI辅助编写部分

---



## 📖 目录

- [功能特点](#-功能特点)
- [快速开始](#-快速开始)
- [项目结构](#-项目结构)
- [核心模块说明](#-核心模块说明)
- [配置说明](#-配置说明)
- [常见问题](#-常见问题)
- [开发指南](#-开发指南)
- [贡献](#-贡献)
- [许可证](#-许可证)
- [免责声明](#-免责声明)

---

## ✨ 功能特点

### 核心功能

- 🎣 **全自动钓鱼** - 自动识别钓鱼游戏界面，控制角色完成抛竿、收杆全流程
- ⚡ **智能耐力检测** - 实时 OCR 识别鱼的耐力值，优化收杆时机
- 🔄 **循环作业** - 自动完成收杆并再次抛竿的循环过程
- 🎯 **精准控制** - 基于颜色识别的鱼位置检测和方向键自动控制

### 技术特性

- 📱 **直观的 Qt UI 界面** - 简洁的操作界面，实时显示钓鱼状态和耐力值
- 🔧 **双 OCR 引擎支持** - 支持 Tesseract 和 PaddleOCR 两种识别引擎
- 🖥️ **后台截图捕获** - 基于 DXGI 的高效窗口截图技术（可选）
- 🛠️ **可配置性强** - 灵活的配置文件调整识别区域和参数
- 📦 **一键打包** - 提供完整的打包脚本，生成独立可执行文件

---

## 🚀 快速开始

### 环境要求

- **操作系统**: Windows 10 1809 及以上版本
- **Python 版本**: Python 3.13
- **游戏窗口**: 幻塔游戏（窗口标题包含"幻塔"二字）
- **权限要求**: **必须以管理员身份运行**（否则无法控制键鼠）

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/nitaichuchong/Hotta_auto_fish.git
cd HottaAutoFish
```

#### 2. 安装依赖

项目使用 `uv` 作为包管理器（推荐使用 uv）：

```bash
# 如果未安装 uv，先安装
pip install uv

# 安装所有依赖
uv sync
```

#### 3. 安装PaddleOCR（可选）

如果需要使用 PaddleOCR 作为识别引擎：

```bash
# 安装PaddlePaddle
python -m pip install paddlepaddle==3.0.0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/

# 安装PaddleOCR
pip install paddleocr
```

### 使用方法

#### 1. 运行程序

**⚠️ 重要：请以管理员身份运行程序！**

```bash
# 运行主程序
python src/main.py
```

#### 2. 操作流程

1. 打开幻塔游戏并进入钓鱼界面
2. 以管理员身份运行本程序
3. 点击"**先点此初始化**"按钮进行初始化
4. 点击"**开始执行**"按钮启动自动钓鱼
5. 观察 UI 界面上的状态显示和耐力值
6. 点击"**停止执行**"按钮结束钓鱼

#### 3. UI 界面说明

- **状态标签** - 显示当前系统状态（未初始化/已就绪/执行中）
- **钓鱼状态** - 显示钓鱼操作状态（自动钓鱼中/已停止等）
- **耐力值显示** - 实时显示当前鱼的耐力值
- **提示信息** - 显示使用说明和注意事项

---

## 📁 项目结构

```
HottaAutoFish/
├── 📄 README.md                          # 项目说明文档
├── 📄 LICENSE                            # MIT 许可证
├── 📄 .gitignore                         # Git 忽略配置
├── 📄 pyproject.toml                     # Python 项目配置文件
├── 📄 uv.lock                            # UV 包管理器锁定文件
│
├── 📂 UI/                                # Qt 界面相关文件
│   ├── .ui/                              # Qt Designer 设计文件
│   │   └── main_window.ui                # 主窗口界面设计
│   ├── .qrc/                             # Qt 资源文件目录
│   ├── __init__.py                       # 包初始化文件
│   └── main_window.py                    # 主窗口 UI 类定义
│
├── 📂 config/                            # 配置文件模块
│   ├── __init__.py                       # 包初始化文件
│   ├── config.py                         # 核心配置文件（游戏区域、颜色阈值等）
│   └── path_manager.py                   # 动态路径管理（兼容开发和打包环境）
│
├── 📂 src/                               # 核心源代码
│   ├── __init__.py                       # 包初始化文件
│   ├── main.py                           # 主程序入口（Qt 主窗口、线程管理）
│   ├── fish_auto.py                      # 钓鱼自动控制逻辑（按键计算）
│   ├── ocr_main.py                       # OCR 识别主逻辑（引擎初始化和调用）
│   ├── sub_threads.py                    # 子线程实现（OCR 线程、钓鱼线程）
│   │
│   └── 📂 utils/                         # 工具函数模块
│       ├── __init__.py                   # 包初始化文件
│       ├── detect_logic.py               # 图像检测逻辑（黄色区域、白色方块识别）
│       ├── dxgi_capture.dll              # DXGI 截图动态库（C++ 编写）
│       ├── dxgi_capture_manager.py       # DXGI 截图管理器
│       ├── input_manager.py              # 输入管理器（后台键鼠控制）
│       ├── mss_capture_manager.py        # MSS 截图管理器（备用方案）
│       ├── ocr_paddle_.py                # PaddleOCR 封装
│       ├── ocr_tesseract.py              # Tesseract OCR 封装
│       └── window_manager.py             # 窗口管理器（置顶、激活）
│
├── 📂 models/                            # OCR 模型文件
│   ├── 📂 PP-OCRv5_mobile_det/           # 文字检测模型
│   │   ├── README.md                     # 模型说明
│   │   ├── config.json                   # 模型配置
│   │   └── inference.yml                 # 推理配置
│   ├── 📂 PP-OCRv5_mobile_rec/           # 中文文字识别模型
│   │   ├── README.md                     # 模型说明
│   │   ├── config.json                   # 模型配置
│   │   └── inference.yml                 # 推理配置
│   ├── 📂 en_PP-OCRv5_mobile_rec/        # 英文文字识别模型
│   │   └── inference.yml                 # 推理配置
│   └── 📂 tesseract/                     # Tesseract OCR 相关
│       └── tessdata/                     # Tesseract 语言数据
│
├── 📂 dxgi_capture/                      # DXGI 截图库源码
│   ├── BUILD.md                          # 构建说明文档
│   ├── CMakeLists.txt                    # CMake 配置文件
│   ├── dllmain.cpp                       # DLL 入口实现
│   ├── pch.cpp                           # 预编译头源文件
│   └── pch.h                             # 预编译头文件
│
├── 📂 test/                              # 测试文件
│   ├── __init__.py                       # 包初始化文件
│   ├── build_test.py                     # 打包测试脚本
│   ├── capture_example.py                # 截图示例脚本
│   ├── detect_test_run.py                # 检测逻辑测试
│   ├── ocr_init_for_build_test.py        # OCR 初始化测试
│   ├── ocr_test.py                       # OCR 识别测试
│   ├── preprocess_frame_test.py          # 图像预处理测试
│   ├── window_find_test.py               # 窗口查找测试
│   ├── 📂 output/                        # 测试输出目录
│   │   └── 1_res.json                    # 测试结果示例
│   └── 📂 preprocess_frame/              # 预处理测试图像
│
├── 📂 utils/                             # 辅助工具
│   ├── __init__.py                       # 包初始化文件
│   ├── build.py                          # PyInstaller 打包脚本
│   ├── get_mouse_coordinate.py           # 鼠标坐标获取工具
│   └── qt_tools.py                       # Qt 相关工具函数
│
├── 📂 ocr_debug/                         # OCR 调试输出目录（运行时生成）
│   └── ...                               # 保存的预处理图像
│
└── 📂 build/                             # 打包输出目录（打包时生成）
    ├── dist/                             # 最终可执行文件
    └── work/                             # 临时编译文件
```

---

## 🔧 核心模块说明

### 1. 主程序模块 (`src/main.py`)

**职责**: 提供 Qt 主窗口和核心控制逻辑

**主要功能**:

- 创建和管理 Qt GUI 界面
- 初始化 OCR 实例
- 管理 OCR 线程和钓鱼线程的启停
- 处理用户交互和状态切换
- 协调各模块之间的通信

**关键类**:

- `MainWindow` - 主窗口类，继承自 QMainWindow
- `StatusEnum` - 状态枚举类（INIT/READY/RUNNING）

### 2. 钓鱼自动控制模块 (`src/fish_auto.py`)

**职责**: 实现钓鱼自动化控制的核心算法

**主要功能**:

- 根据黄色区域中心点与玩家位置的偏移计算需要按下的方向键
- 提供 X 坐标偏移计算功能
- 支持阈值控制，避免频繁按键

**关键函数**:

- `key_to_press()` - 获取当前需要按下的按键（'a'/'d'/''）
- `calculate_the_offset_x()` - 计算 X 坐标偏移值

### 3. OCR 识别模块 (`src/ocr_main.py`)

**职责**: 提供 OCR 识别功能，支持双引擎

**主要功能**:

- 初始化 Tesseract 或 PaddleOCR 引擎
- 执行 OCR 识别，返回耐力值
- 支持调试模式，保存预处理图像

**支持的引擎**:

- **Tesseract** - 轻量级，默认引擎
- **PaddleOCR** - 高精度，可选引擎

### 4. 子线程模块 (`src/sub_threads.py`)

**职责**: 提供后台执行的线程实现

**主要类**:

- `BaseThread` - 基础线程类，提供暂停/恢复/停止功能
- `OCRThread` - OCR 识别线程，持续识别耐力值
- `FishThread` - 钓鱼控制线程，根据耐力值和图像检测控制按键

**线程特性**:

- 使用 Qt 的信号槽机制进行线程间通信
- 支持优雅的暂停和恢复
- 完善的异常处理和错误报告

### 5. 配置模块 (`config/config.py`)

**职责**: 提供项目所需的所有配置常量

**主要配置项**:

| 配置项                     | 说明          | 默认值                  |
| ----------------------- | ----------- | -------------------- |
| `FISH_GAME_REGION`      | 钓鱼游戏体力条区域   | `(650, 60, 750, 40)` |
| `FISH_ENDURANCE_REGION` | 鱼的耐力值区域     | `(640, 115, 50, 20)` |
| `YELLOW_LOW`            | 黄色像素 HSV 下限 | `(18, 183, 235)`     |
| `YELLOW_HIGH`           | 黄色像素 HSV 上限 | `(19, 191, 255)`     |
| `WHITE_BLOCK_AREA_MIN`  | 白色方块最小面积    | `10`                 |
| `WHITE_BLOCK_AREA_MAX`  | 白色方块最大面积    | `100`                |
| `WHITE_BLOCK_SOLIDITY`  | 白色方块实度阈值    | `0.5`                |
| `OFFSET_THRESHOLD`      | 执行控制的偏移阈值   | `10`                 |
| `OCR_TYPE`              | OCR 引擎选择    | `"tesseract"`        |
| `OCR_DEBUG`             | OCR 调试开关    | `False`              |

### 6. 路径管理模块 (`config/path_manager.py`)

**职责**: 动态管理路径，兼容开发环境和打包环境

**主要函数**:

- `get_project_path()` - 获取项目根目录
- `get_tesseract_path()` - 获取 Tesseract 可执行文件目录
- `get_tessdata_prefix()` - 获取 Tesseract 语言数据目录
- `get_dxgi_capture_dll_path()` - 获取 DXGI 截图 DLL 路径

**特性**:

- 自动识别开发环境和 PyInstaller 打包后的环境
- 确保路径在不同环境下都能正确定位

### 7. 图像检测模块 (`src/utils/detect_logic.py`)

**职责**: 提供图像预处理和目标检测功能

**主要功能**:

- 黄色区域检测（用于识别鱼的体力条）
- 白色方块检测（用于识别玩家位置）
- 图像预处理（灰度化、二值化、形态学操作等）
- 截图管理（支持 DXGI 和 MSS 两种方式）

**关键函数**:

- `get_yellow_area_range()` - 获取黄色区域的左右边界
- `get_white_block_pos()` - 获取白色方块的 X 坐标位置

### 8. 输入管理模块 (`src/utils/input_manager.py`)

**职责**: 提供后台键鼠控制功能

**主要功能**:

- 后台键盘按键模拟
- 后台鼠标操作
- 支持 DXGI 截图模式下的输入控制

**特性**:

- 使用 Windows API 实现后台输入
- 不需要窗口在前台即可操作
- 避免干扰用户正常使用其他窗口

### 9. 窗口管理模块 (`src/utils/window_manager.py`)

**职责**: 提供窗口操作功能

**主要功能**:

- 设置窗口置顶（软置顶）
- 激活游戏窗口
- 检查窗口是否在前台

**关键函数**:

- `set_window_topmost()` - 使用 Windows API 设置窗口置顶
- `activate_game_window()` - 激活游戏窗口
- `is_window_foreground()` - 检查窗口是否在前台

### 10. DXGI 截图库 (`dxgi_capture/`)

**职责**: 提供高效的窗口截图功能

**技术栈**:

- **语言**: C++
- **API**: Windows.Graphics.Capture, Direct3D 11
- **优化**: AVX2 加速内存复制

**构建方法**: 详见 [`dxgi_capture/BUILD.md`](dxgi_capture/BUILD.md)

**系统要求**:

- Windows 10 1809 及以上版本
- 支持 DirectX 11 的显卡
- Visual Studio 2019+ 和 CMake 3.16+

### 11. 打包工具 (`utils/build.py`)

**职责**: 使用 PyInstaller 将项目打包为可执行文件

**主要功能**:

- 清理旧的打包文件
- 配置 PyInstaller 参数
- 添加模型文件和 DLL 依赖
- 处理 PaddleX 和 Qt 相关依赖

**使用方法**:

```bash
python utils/build.py
```

**输出目录**: `build/dist/HottaAutoFish/`

---

## ⚙️ 配置说明

### 如何调整识别区域

1. **获取鼠标坐标**
   运行工具脚本获取屏幕坐标：
   
   ```bash
   python utils/get_mouse_coordinate.py
   ```

2. **修改配置文件**
   编辑 `config/config.py`，调整以下配置：
   
   ```python
   # 钓鱼游戏体力条的区域范围
   FISH_GAME_REGION: tuple[int, int, int, int] = (left, top, width, height)
   
   # 鱼的耐力值的区域范围
   FISH_ENDURANCE_REGION: tuple[int, int, int, int] = (left, top, width, height)
   ```

3. **保存并重启程序**

### 分辨率适配

默认配置适用于 **1920x1080** 分辨率。如果使用其他分辨率：

1. 使用 `get_mouse_coordinate.py` 获取目标区域的坐标
2. 根据获取的坐标修改 `config/config.py` 中的区域配置
3. 可能需要调整颜色阈值以适应不同的显示效果

### OCR 引擎切换

在 `config/config.py` 中修改：

```python
# 使用 Tesseract（默认）
OCR_TYPE: str = "tesseract"

# 使用 PaddleOCR
OCR_TYPE: str = "paddle"
```

**注意**: 使用 PaddleOCR 需要先安装相关依赖。

### 调试模式

开启 OCR 调试模式可以保存预处理后的图像，便于调整参数：

```python
# 开启调试模式
OCR_DEBUG: bool = True
```

调试图像将保存在 `ocr_debug/` 目录下。

---

## ❓ 常见问题

### 1. 无法控制游戏

**原因**: 程序没有以管理员身份运行

**解决方法**: 

- 右键点击命令行工具或 IDE，选择"以管理员身份运行"
- 然后再运行程序

### 2. 识别不准确

**可能原因**:

- 识别区域配置不正确
- 游戏分辨率与默认配置不同
- 颜色阈值不适合当前显示效果

**解决方法**:

- 使用 `get_mouse_coordinate.py` 重新获取坐标
- 调整 `config/config.py` 中的区域配置
- 如有必要，调整颜色 HSV 范围

### 3. 程序崩溃

**可能原因**:

- 缺少必要的依赖
- OCR 引擎未正确安装
- 游戏窗口未找到

**解决方法**:

- 检查是否安装了所有依赖
- 确认 PaddleOCR 或 Tesseract 已正确安装
- 确保游戏窗口标题包含"幻塔"二字

### 4. OCR 识别失败

**可能原因**:

- Tesseract 路径配置错误
- 语言包缺失
- PaddleOCR 模型文件缺失

**解决方法**:

- 检查 `config/path_manager.py` 中的路径配置
- 确认 `models/tesseract/tessdata/` 目录下有语言包文件
- 确认 `models/` 目录下的 PaddleOCR 模型文件完整

### 5. 打包后运行报错

**常见问题**:

- 路径中包含中文（特别是 pytesseract）
- 某些隐性导入未被识别

**解决方法**:

- 确保打包路径不包含中文字符
- 检查 `utils/build.py` 中的 `--hidden-import` 配置
- 查看错误信息，手动添加缺失的模块

---

## 🛠️ 开发指南

### 开发环境搭建

1. **安装 Python 3.13**

2. **安装依赖**
   
   ```bash
   uv sync
   ```

3. **安装PaddleOCR（可选）**
   
   ```bash
   python -m pip install paddlepaddle==3.0.0 -i https://www.paddlepaddle.org.cn/packages/stable/cpu/
   pip install paddleocr
   ```

### 代码规范

- **命名风格**: 变量和函数名使用 camelCase 格式
- **注释**: 保留原有注释，新增注释使用中文
- **类型提示**: 鼓励使用类型注解
- **代码整洁**: 遵循 DRY 原则，避免重复代码

### 测试

运行测试脚本：

```bash
# OCR 测试
python test/ocr_test.py

# 检测逻辑测试
python test/detect_test_run.py

# 窗口查找测试
python test/window_find_test.py
```

### 构建 DXGI 截图库

详见 [`dxgi_capture/BUILD.md`](dxgi_capture/BUILD.md)

简要步骤：

```bash
cd dxgi_capture
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

将生成的 `dxgi_capture.dll` 复制到 `src/utils/` 目录。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 贡献方式

- 🐛 报告 Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码修复或改进

### 贡献流程

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 **MIT 许可证**，详见 [LICENSE](LICENSE) 文件。

---

## ⚠️ 免责声明

本工具仅用于**学习和研究**目的。

- 请勿将本工具用于任何违反游戏规则的行为
- 请勿将本工具用于任何违反法律法规的活动
- 使用本工具产生的一切后果由使用者**自行承担**
- 本项目作者不对使用本工具产生的任何损失负责

---

## 🙏 致谢

感谢以下开源项目：

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- [PySide6](https://doc.qt.io/qtforpython/)
- [OpenCV](https://opencv.org/)
- [PyInstaller](https://www.pyinstaller.org/)

---

<div align="center">

**Made with ❤️ by the HottaAutoFish Team**

如果这个项目对你有帮助，请给一个 ⭐ Star！

</div>
