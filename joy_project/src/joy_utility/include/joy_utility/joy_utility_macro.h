#pragma once
#ifdef JOY_UTILITY_DLL
    #if _WIN32
        #define JOY_UTILITY_API __declspec(dllexport)
    #else
        #define JOY_UTILITY_API
    #endif
#else
    #if _WIN32
        #define JOY_UTILITY_API __declspec(dllimport)
        #ifdef _DEBUG
            #pragma comment(lib,"joy_utility_d.lib")
            #pragma message("auto linking to joy_utility_d.lib")
        #else
            #pragma comment(lib,"joy_utility.lib")
            #pragma message("auto linking to joy_utility.lib")
        #endif
    #else
        #define JOY_UTILITY_API
    #endif
#endif

#define _JOY_UTILITY_BEGIN_ namespace JOY_UTILITY {
#define _JOY_UTILITY_END_   }

#define UNUSED_ALWAYS(P) (P)
#define safe_delete_array(p) (delete[](p), (p) = nullptr)
#define safe_delete(p) (delete (p), (p) = nullptr)

#ifndef _CUR_FUNCTION_
    #ifdef __GNUC__ // GCC/Clang
    `   #define _CUR_FUNCTION_ __PRETTY_FUNCTION__
    #elif _MSC_VER // MSVC
        #define _CUR_FUNCTION_  __FUNCSIG__
    #endif
    #define STRINGIFY_IMPL(x) #x         // 内层宏：参数字符串化
    #define STRINGIFY(x) STRINGIFY_IMPL(x) // 外层宏：确保参数展开
    #define COMBINE_SIG_LINE(PREFIX) PREFIX _CUR_FUNCTION_ " @ Line: " STRINGIFY(__LINE__)
#endif

