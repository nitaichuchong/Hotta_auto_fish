// pch.h: This is a precompiled header file.

#ifndef PCH_H
#define PCH_H

// Windows Header Files
#include <windows.h>

// DirectX Headers
#include <dxgi1_2.h>
#include <d3d11.h>

// Windows Runtime Headers
#include <winrt/Windows.Foundation.h>
#include <winrt/Windows.System.h>
#include <winrt/Windows.Graphics.Capture.h>
#include <windows.graphics.capture.interop.h>
#include <windows.graphics.directx.direct3d11.interop.h>

// Other Headers
#include <dwmapi.h>
#include <chrono>
#include <thread>

// Libraries
#pragma comment(lib, "Dwmapi.lib")
#pragma comment(lib, "windowsapp.lib")

// Forward declaration
class DXGICapture;

// Global capture instance
extern DXGICapture* g_capture;

// Exported Functions
extern "C" __declspec(dllexport) void init_capture(HWND hwnd);
extern "C" __declspec(dllexport) unsigned char* capture_window(unsigned char* buffer, int left, int top, int width, int height);
extern "C" __declspec(dllexport) void cleanup();

#endif // PCH_H