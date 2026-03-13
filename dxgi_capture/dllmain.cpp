// dllmain.cpp : Defines the entry point for the DLL application.
#include "pch.h"

BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
                     )
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
        // DLL is being loaded into a process's address space
        break;
    case DLL_THREAD_ATTACH:
        // A thread is being created in the process
        break;
    case DLL_THREAD_DETACH:
        // A thread is exiting cleanly
        break;
    case DLL_PROCESS_DETACH:
        // DLL is being unloaded from a process's address space
        // Cleanup capture instance if it exists
        if (g_capture) {
            delete g_capture;
            g_capture = nullptr;
        }
        break;
    }
    return TRUE;
}