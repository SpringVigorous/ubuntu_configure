#pragma once
#ifdef DATA_DLL
    #if _WIN32
        #define DATA_API __declspec(dllexport)
    #else
        #define DATA_API
    #endif
#else
    #if _WIN32
        #define DATA_API __declspec(dllimport)
        #ifdef _DEBUG
            #pragma comment(lib,"data_d.lib")
            #pragma message("auto linking to data_d.lib")
        #else
            #pragma comment(lib,"data.lib")
            #pragma message("auto linking to data.lib")
        #endif
    #else
        #define DATA_API
    #endif
#endif

#define _DATA_BEGIN_ namespace DATA {
#define _DATA_END_   }

