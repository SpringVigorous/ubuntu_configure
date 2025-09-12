#pragma once
#ifdef HANDLE_DATA_DLL
    #if _WIN32
        #define HANDLE_DATA_API __declspec(dllexport)
    #else
        #define HANDLE_DATA_API
    #endif
#else
    #if _WIN32
        #define HANDLE_DATA_API __declspec(dllimport)
        #ifdef _DEBUG
            #pragma comment(lib,"handle_data_d.lib")
            #pragma message("auto linking to handle_data_d.lib")
        #else
            #pragma comment(lib,"handle_data.lib")
            #pragma message("auto linking to handle_data.lib")
        #endif
    #else
        #define HANDLE_DATA_API
    #endif
#endif

#define _HANDLE_DATA_BEGIN_ namespace HANDLE_DATA {
#define _HANDLE_DATA_END_   }

