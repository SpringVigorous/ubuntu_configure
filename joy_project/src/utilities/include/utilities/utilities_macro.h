#pragma once
#ifdef UTILITIES_DLL
    #if _WIN32
        #define UTILITIES_API __declspec(dllexport)
    #else
        #define UTILITIES_API
    #endif
#else
    #if _WIN32
        #define UTILITIES_API __declspec(dllimport)
        #ifdef _DEBUG
            #pragma comment(lib,"utilities_d.lib")
            #pragma message("auto linking to utilities_d.lib")
        #else
            #pragma comment(lib,"utilities.lib")
            #pragma message("auto linking to utilities.lib")
        #endif
    #else
        #define UTILITIES_API
    #endif
#endif

#define _UTILITIES_BEGIN_ namespace UTILITIES {
#define _UTILITIES_END_   }

