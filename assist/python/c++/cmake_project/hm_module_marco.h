#pragma once
#ifdef HM_MODULE_DLL
    #if _WIN32
        #define HM_MODULE_API __declspec(dllexport)
    #else
        #define HM_MODULE_API
    #endif
#else
    #if _WIN32
        #define HM_MODULE_API __declspec(dllimport)
        #ifdef _DEBUG
            #pragma comment(lib,"hm_module_d.lib")
            #pragma message("auto linking to hm_module_d.lib")
        #else
            #pragma comment(lib,"hm_module.lib")
            #pragma message("auto linking to hm_module.lib")
        #endif
    #else
        #define HM_MODULE_API
    #endif
#endif

#define _HM_MODULE_BEGIN_ namespace HM_MODULE {
#define _HM_MODULE_END_   }

