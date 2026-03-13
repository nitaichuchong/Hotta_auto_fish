// pch.cpp: source file corresponding to the pre-compiled header

#include "pch.h"

// AVX2 optimized memory copy function
void optimized_memcpy(unsigned char* dst, unsigned char* src, size_t size)
{
    if (dst != src) {
        // Check if addresses are 32-byte aligned for AVX2
        bool src_aligned = ((reinterpret_cast<uintptr_t>(src) & 0x1F) == 0);
        bool dst_aligned = ((reinterpret_cast<uintptr_t>(dst) & 0x1F) == 0);
        
        if (src_aligned && dst_aligned) {
            // Use AVX2 for aligned memory
            size_t vectors = size / 32;
            size_t residual = size % 32;
            
            __m256i* src_vec = reinterpret_cast<__m256i*>(src);
            __m256i* dst_vec = reinterpret_cast<__m256i*>(dst);
            
            for (size_t i = 0; i < vectors; i++) {
                __m256i data = _mm256_load_si256(src_vec + i);
                _mm256_store_si256(dst_vec + i, data);
            }
            
            // Copy remaining bytes
            if (residual > 0) {
                memcpy(dst + vectors * 32, src + vectors * 32, residual);
            }
        } else {
            // Use standard memcpy for unaligned memory
            memcpy(dst, src, size);
        }
    }
}

class DXGICapture {
public:
    DXGICapture(HWND hwnd);
    ~DXGICapture();
    unsigned char* Capture(unsigned char* buffer, int left, int top, int width, int height);
    
private:
    void Initialize();
    void Cleanup();
    
    HWND hwnd_target;
    bool is_initialized;
    bool frame_arrived;
    
    // Direct3D resources
    winrt::com_ptr<ID3D11Device> d3d_device;
    winrt::com_ptr<ID3D11DeviceContext> d3d_context;
    winrt::com_ptr<ID3D11Texture2D> captured_texture;
    
    // Windows Graphics Capture resources
    winrt::Windows::Graphics::Capture::GraphicsCaptureSession capture_session{ nullptr };
    winrt::Windows::Graphics::Capture::Direct3D11CaptureFramePool frame_pool{ nullptr };
};

DXGICapture::DXGICapture(HWND hwnd) : 
    hwnd_target(hwnd), 
    is_initialized(false), 
    frame_arrived(false),
    capture_session(nullptr),
    frame_pool(nullptr)
{
    Initialize();
}

DXGICapture::~DXGICapture()
{
    Cleanup();
}

void DXGICapture::Initialize()
{
    try {
        // Initialize COM
        winrt::init_apartment(winrt::apartment_type::multi_threaded);
        
        // Create D3D11 device with BGRA support
        HRESULT hr = D3D11CreateDevice(
            nullptr,                          // Use default adapter
            D3D_DRIVER_TYPE_HARDWARE,        // Use hardware rendering
            nullptr,                          // No software rasterizer
            D3D11_CREATE_DEVICE_BGRA_SUPPORT, // Enable BGRA support
            nullptr,                          // No feature levels specified
            0,                                // Number of feature levels
            D3D11_SDK_VERSION,                // SDK version
            d3d_device.put(),                 // Device pointer
            nullptr,                          // Feature level used
            d3d_context.put()                 // Device context
        );
        
        if (FAILED(hr)) {
            return;
        }
        
        // Get window size
        RECT window_rect;
        DwmGetWindowAttribute(hwnd_target, DWMWA_EXTENDED_FRAME_BOUNDS, &window_rect, sizeof(RECT));
        int width = window_rect.right - window_rect.left;
        int height = window_rect.bottom - window_rect.top;
        
        if (width <= 0 || height <= 0) {
            return;
        }
        
        // Create Direct3D device for Windows.Graphics.Capture
        winrt::Windows::Graphics::DirectX::Direct3D11::IDirect3DDevice device;
        auto dxgi_device = d3d_device.as<IDXGIDevice>();
        
        winrt::com_ptr<::IInspectable> inspectable;
        hr = CreateDirect3D11DeviceFromDXGIDevice(dxgi_device.get(), inspectable.put());
        if (FAILED(hr)) {
            return;
        }
        
        inspectable.as(device);
        
        // Create frame pool
        frame_pool = winrt::Windows::Graphics::Capture::Direct3D11CaptureFramePool::CreateFreeThreaded(
            device,
            winrt::Windows::Graphics::DirectX::DirectXPixelFormat::B8G8R8A8UIntNormalized,
            1,  // Number of buffers
            { width, height }  // Size
        );
        
        // Create capture item from window
        const auto activation_factory = winrt::get_activation_factory<winrt::Windows::Graphics::Capture::GraphicsCaptureItem>();
        auto interop_factory = activation_factory.as<IGraphicsCaptureItemInterop>();
        
        winrt::Windows::Graphics::Capture::GraphicsCaptureItem capture_item(nullptr);
        hr = interop_factory->CreateForWindow(
            hwnd_target,
            winrt::guid_of<ABI::Windows::Graphics::Capture::IGraphicsCaptureItem>(),
            winrt::put_abi(capture_item)
        );
        
        if (FAILED(hr)) {
            return;
        }
        
        // Create capture session
        capture_session = frame_pool.CreateCaptureSession(capture_item);
        
        // Set up frame arrived event handler
        frame_pool.FrameArrived([this](auto& sender, auto& args) {
            auto frame = sender.TryGetNextFrame();
            if (frame) {
                auto surface = frame.Surface();
                auto access = surface.as<Windows::Graphics::DirectX::Direct3D11::IDirect3DDxgiInterfaceAccess>();
                access->GetInterface(winrt::guid_of<ID3D11Texture2D>(), captured_texture.put_void());
                frame_arrived = true;
            }
        });
        
        // Start capture
        capture_session.IsCursorCaptureEnabled(false);
        capture_session.StartCapture();
        
        is_initialized = true;
    } catch (...) {
        // Handle exceptions
        is_initialized = false;
    }
}

void DXGICapture::Cleanup()
{
    if (capture_session) {
        capture_session.Close();
        capture_session = nullptr;
    }
    
    frame_pool = nullptr;
    captured_texture = nullptr;
    d3d_context = nullptr;
    d3d_device = nullptr;
    
    is_initialized = false;
    frame_arrived = false;
}

unsigned char* DXGICapture::Capture(unsigned char* buffer, int left, int top, int width, int height)
{
    if (!is_initialized) {
        return nullptr;
    }
    
    // Wait for frame to arrive
    int timeout = 1000; // 1 second timeout
    int elapsed = 0;
    
    while (!frame_arrived && elapsed < timeout) {
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
        elapsed++;
    }
    
    if (!frame_arrived || !captured_texture) {
        return nullptr;
    }
    
    frame_arrived = false;
    
    try {
        // Get texture description
        D3D11_TEXTURE2D_DESC desc;
        captured_texture->GetDesc(&desc);
        
        // Create staging texture for CPU access
        D3D11_TEXTURE2D_DESC staging_desc = desc;
        staging_desc.Usage = D3D11_USAGE_STAGING;
        staging_desc.BindFlags = 0;
        staging_desc.CPUAccessFlags = D3D11_CPU_ACCESS_READ;
        staging_desc.MiscFlags = 0;
        staging_desc.Width = width;
        staging_desc.Height = height;
        
        winrt::com_ptr<ID3D11Texture2D> staging_texture;
        HRESULT hr = d3d_device->CreateTexture2D(&staging_desc, nullptr, staging_texture.put());
        
        if (FAILED(hr)) {
            return nullptr;
        }
        
        // Copy subresource region
        D3D11_BOX source_region;
        source_region.left = left;
        source_region.top = top;
        source_region.right = left + width;
        source_region.bottom = top + height;
        source_region.front = 0;
        source_region.back = 1;
        
        d3d_context->CopySubresourceRegion(
            staging_texture.get(),  // Destination
            0,                      // Destination subresource
            0, 0, 0,               // Destination offset
            captured_texture.get(), // Source
            0,                      // Source subresource
            &source_region          // Source region
        );
        
        // Map texture to CPU memory
        D3D11_MAPPED_SUBRESOURCE mapped_resource;
        hr = d3d_context->Map(staging_texture.get(), 0, D3D11_MAP_READ, 0, &mapped_resource);
        
        if (FAILED(hr)) {
            return nullptr;
        }
        
        // Calculate row pitch
        UINT bmp_row_pitch = width * 4; // 4 bytes per pixel (BGRA)
        UINT row_pitch = std::min<UINT>(bmp_row_pitch, mapped_resource.RowPitch);
        
        // Copy data to buffer
        unsigned char* src_ptr = static_cast<unsigned char*>(mapped_resource.pData);
        unsigned char* dst_ptr = buffer;
        
        for (int h = 0; h < height; h++) {
            optimized_memcpy(dst_ptr, src_ptr, row_pitch);
            src_ptr += mapped_resource.RowPitch;
            dst_ptr += bmp_row_pitch;
        }
        
        // Unmap texture
        d3d_context->Unmap(staging_texture.get(), 0);
        
        return buffer;
    } catch (...) {
        return nullptr;
    }
}

// Global capture instance
DXGICapture* g_capture = nullptr;

// Exported functions
extern "C" __declspec(dllexport) void init_capture(HWND hwnd)
{
    // Cleanup any existing instance
    if (g_capture) {
        delete g_capture;
        g_capture = nullptr;
    }
    
    // Create new capture instance
    g_capture = new DXGICapture(hwnd);
}

extern "C" __declspec(dllexport) unsigned char* capture_window(unsigned char* buffer, int left, int top, int width, int height)
{
    if (g_capture) {
        return g_capture->Capture(buffer, left, top, width, height);
    }
    return nullptr;
}

extern "C" __declspec(dllexport) void cleanup()
{
    if (g_capture) {
        delete g_capture;
        g_capture = nullptr;
    }
}