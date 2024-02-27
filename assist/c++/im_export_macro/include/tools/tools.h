#pragma once
#if _WIN32
    #ifdef __TOOLS__
        #define TOOLS_API __declspec(dllexport)
    #else
        #define TOOLS_API __declspec(dllimport)
    #endif
#else
    #define TOOLS_API
#endif

#define _TOOLS_BEGIN_ \
    namespace TOOLS   \
    {
#define _TOOLS_END_ }