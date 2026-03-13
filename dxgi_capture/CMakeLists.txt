cmake_minimum_required(VERSION 3.16)

project(dxgi_capture LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR})

# Add source files
set(SOURCE_FILES
    dllmain.cpp
    pch.cpp
)

# Add header files
set(HEADER_FILES
    pch.h
)

# Create DLL
add_library(dxgi_capture SHARED ${SOURCE_FILES} ${HEADER_FILES})

# Set DLL export properties
set_target_properties(dxgi_capture PROPERTIES
    WINDOWS_EXPORT_ALL_SYMBOLS ON
    MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>"
)

# Link against required libraries
target_link_libraries(dxgi_capture PRIVATE
    Dwmapi.lib
    windowsapp.lib
    d3d11.lib
    dxgi.lib
)

# Enable AVX2 instructions if supported
if(CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
    target_compile_options(dxgi_capture PRIVATE /arch:AVX2)
elseif(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(dxgi_capture PRIVATE -mavx2)
endif()
