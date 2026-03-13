# dxgi\_capture 项目构建说明

本文档详细介绍了如何使用 CMake 构建 dxgi\_capture 项目。

## 项目简介

dxgi\_capture 是一个基于 DXGI (DirectX Graphics Infrastructure) 的窗口捕获库，通过 C++ DLL 实现高效的窗口截图功能。

## 系统要求

- **操作系统**: Windows 10 1809 及以上版本 (64位)
- **硬件**: 支持 DirectX 11 的显卡
- **开发环境**: Visual Studio 2019 或更高版本
- **CMake**: 3.16 或更高版本

## 系统依赖

### 1. Visual Studio

- 安装 Visual Studio 2019 或更高版本
- 安装时必须包含 "C++ 桌面开发" 工作负载
- 确保安装了最新的 Windows SDK

### 2. Windows SDK

- 版本要求: 10.0.18362.0 或更高版本
- 包含以下组件:
  - Windows SDK for Desktop C++
  - DirectX SDK (通常包含在 Windows SDK 中)

## CMake 构建步骤

### 1. 准备项目

确保你已经在 `dxgi_capture` 目录下，该目录应包含以下文件:

- `CMakeLists.txt`
- `dllmain.cpp`
- `pch.cpp`
- `pch.h`

### 2. 创建构建目录

打开命令提示符或 PowerShell，执行以下命令:

```bash
# 进入项目目录
cd .\dxgi_capture

# 创建构建目录
mkdir build
cd build
```

### 3. 配置 CMake

执行 CMake 配置命令，生成 Visual Studio 解决方案:

```bash
cmake ..
```

此命令会在 `build` 目录中生成 `dxgi_capture.sln` 解决方案文件。

### 4. 构建项目

使用 CMake 构建命令编译项目:

```bash
cmake --build . --config Release
```

此命令会在 `build\Release` 目录中生成 `dxgi_capture.dll` 文件。

### 5. 复制 DLL 文件

将生成的 DLL 文件复制到需要的位置

# 

## 构建过程中的常见问题

### 1. CMake 找不到 Visual Studio

- **原因**: Visual Studio 未正确安装或环境变量未设置
- **解决方法**: 确保 Visual Studio 已正确安装，并尝试使用 `cmake -G "Visual Studio 16 2019" ..` 指定具体的 Visual Studio 版本

### 2. 缺少 Windows SDK

- **原因**: 未安装 Windows SDK 或版本过低
- **解决方法**: 安装 10.0.18362.0 或更高版本的 Windows SDK

### 3. 缺少 DirectX 头文件

- **原因**: DirectX SDK 未正确安装
- **解决方法**: 确保安装了包含 DirectX 组件的 Windows SDK

### 4. 编译错误

- **原因**: 代码中的语法错误或依赖问题
- **解决方法**: 查看编译错误信息，根据提示修复代码问题

## 技术细节

### 核心技术

- **Windows.Graphics.Capture API**: 用于高效捕获窗口内容
- **Direct3D 11**: 用于图形资源管理
- **AVX2 优化**: 加速内存复制

### 性能优化

- 使用硬件加速的 DirectX 捕获
- 优化的内存复制操作
- 异步帧捕获

## 注意事项

- 仅支持 Windows 10 1809 及以上版本
- 某些受保护的应用程序可能无法捕获
- 高分辨率捕获可能会增加内存使用

## 结语

通过本说明文档，你应该能够成功使用 CMake 构建 dxgi\_capture 项目。如果遇到问题，请参考常见问题部分或检查系统要求。
