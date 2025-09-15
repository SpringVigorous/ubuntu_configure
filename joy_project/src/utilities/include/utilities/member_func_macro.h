#pragma once
#ifndef __UTILITIES_MEMBER_FUNC_MACRO_H__
#define __UTILITIES_MEMBER_FUNC_MACRO_H__


// 通用模板宏（基础功能）
#define HAS_MEM_FUNC_BASE(func_name) \
template <typename T, typename... Args> \
struct has_##func_name##_impl { \
    static constexpr bool value = requires(T a, Args... args) { \
        a.func_name(args...); \
    }; \
}; \
template <typename T, typename... Args> \
inline constexpr bool has_##func_name##_v = has_##func_name##_impl<T, Args...>::value;

//带参数的成员函数
#define HAS_MEM_FUNC_WITH_ARGS(func_name,lat,...) \
    /*HAS_MEM_FUNC_BASE(func_name)*/ \
    template <typename T> \
    inline constexpr bool has_##func_name##_##lat##_v = has_##func_name##_v<T,__VA_ARGS__>;


#define HAS_MEM_FUNC_BASE_WITH_ARGS(func_name,lat,...) \
    HAS_MEM_FUNC_BASE(func_name) \
    HAS_MEM_FUNC_WITH_ARGS(func_name,lat,__VA_ARGS__)


//不带参数的成员函数
#define HAS_MEM_FUNC_NO_ARGS(func_name,lat) \
    /*HAS_MEM_FUNC_BASE(func_name)*/ \
    template <typename T> \
    inline constexpr bool has_##func_name##_##lat##_v = has_##func_name##_v<T>;



#define HAS_MEM_FUNC_BASE_NO_ARGS(func_name,lat) \
    HAS_MEM_FUNC_BASE(func_name) \
    HAS_MEM_FUNC_NO_ARGS(func_name,lat)




/*用法,
* eg:::serialize_members(member_rw_interface & mt)
用宏条件编译限定

#ifndef HAS_SERIALIZE_MEMBERS_FUNCTION
    #define HAS_SERIALIZE_MEMBERS_FUNCTION
    HAS_MEM_FUNC_BASE_WITH_ARGS(serialize_members, func, member_rw_interface&);
#endif

后续使用（模版中）：
    if constexpr (has_serialize_members_func_v<T>)

*/

#endif
